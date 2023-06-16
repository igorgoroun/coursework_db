from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
import logging
from product.product import _list as _product_list, _search_by_name as _search_product_by_name
from .move import _list_for_order as _list_moves_for_order
from . import ORDER_DB_TABLE, STOCK_DB_TABLE

_logger = logging.getLogger(__name__)
order_app = Blueprint('order_page', __name__, template_folder='templates')


def _list_orders(order_type='sale', **kwargs):
    query = """
        select o.*, 
            p.name as partner_name,
            (select sum(m.unit_price * m.qty_draft) from multimove m where m.order_id=o.id) as total_amount
        from multiorder o
        left join partner p on p.id = o.partner_id
        where 1=1
            and o.type=%s
        order by o.deadline_date desc
    """
    return cr.search(query, params=(order_type, ))


def _get_detail(order_id, product_name=False, **kwargs) -> dict:
    order = cr.read(table_name=ORDER_DB_TABLE, record_id=order_id, fields=('id', 'type', 'partner_id', 'incoterm', 'payment_term', 'state', 'create_date', 'deadline_date'))
    if not order:
        abort(404)

    # available product list
    products = None
    if product_name:
        products = _search_product_by_name(product_name=product_name)

    moves = _list_moves_for_order(order_id)

    return {
        'order': order,
        'type': order.get('type', 'sale'),
        'product_name': product_name or '',
        'products': products,
        'partner': cr.read(table_name='partner', record_id=order.get('partner_id'), fields=('id', 'name')),
        'moves': moves,
        'total_amount': sum([m.get('amount') for m in moves])
    }


@order_app.route('/route/<int:order_id>/pay/', methods=['GET'])
def view_confirm_payment(order_id):
    order = cr.read(table_name=ORDER_DB_TABLE, record_id=order_id)
    if not all([
        order,
        # order.get('type') == 'purchase',
        # order.get('state', 'draft') == 'draft'
    ]):
        abort(404)
    new_state = 'done'
    if order.get('payment_term') == 'on_invoice':
        new_state = 'await_delivery'
    cr.write(ORDER_DB_TABLE, order_id, state=new_state)
    return redirect(url_for('order_page.view_detail', order_id=order_id))


@order_app.route('/order/<int:order_id>/confirm/', methods=['GET'])
def view_confirm(order_id):
    order = cr.read(ORDER_DB_TABLE, order_id)
    if not all([
        order,
        # order.get('type') == 'purchase',
        order.get('state', 'draft') == 'draft']
    ):
        abort(404)
    new_po_state = 'await_payment'
    if order.get('payment_term') == 'on_delivery':
        new_po_state = 'await_delivery'
    cr.write(ORDER_DB_TABLE, order_id, state=new_po_state)
    return redirect(url_for('order_page.view_detail', order_id=order_id))


@order_app.route('/purchase/<int:order_id>/', methods=['GET'])
def view_detail(order_id):
    product_name = request.args.get('product_name', False)
    data = _get_detail(order_id=order_id, product_name=product_name)
    if not data:
        abort(404)

    return render_template(
        template_name_or_list='order/detail.html',
        page_title='Ордер на закупівлю' if data.get('type') == 'purchase' else 'Ордер на продаж',
        **data
    )


@order_app.route('/order/<int:order_id>/delete/', methods=['GET'])
def view_delete(order_id):
    order = cr.read(ORDER_DB_TABLE, order_id)
    if order.get('state', 'draft') != 'draft':
        return redirect(url_for('order_page.view_list'))
    if cr.unlink(table_name="order", record_id=order_id):
        return redirect(url_for('order_page.view_list'))
