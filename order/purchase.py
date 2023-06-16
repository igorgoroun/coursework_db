from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
from .order import _list_orders, _get_detail
from partner import (
    PAYMENT_TERMS,
    INCOTERMS
)
from partner.partner import _list as _partners_list
from . import ORDER_DB_TABLE, STOCK_DB_TABLE
import logging

_logger = logging.getLogger(__name__)

purchase_app = Blueprint('purchase_page', __name__, template_folder='templates')


@purchase_app.route('/purchase/<int:order_id>/receive/', methods=['POST', 'GET'])
def view_receive(order_id):
    order = cr.read(table_name=ORDER_DB_TABLE, record_id=order_id, fields=('id', 'type', 'payment_term'))
    if not all([order, order.get('type', False) == 'purchase']):
        abort(404)

    lines = cr.search(query="""
        select id, product_id, unit_price, qty_draft, qty_done
        from multimove
        where order_id=%s and confirmed is false
    """, params=(order_id, ))

    _logger.warning(f"IN list: {[l.get('id') for l in lines]}")

    if request.method == 'POST':
        move_qty = dict(zip(request.form.getlist('move_id'), request.form.getlist('qty_done')))
        # update moves
        for move_id, move_qty_done in move_qty.items():
            _logger.warning(f"Move: {move_id}, QTY_DONE: {move_qty_done}")
            if int(move_id) in [l.get('id') for l in lines]:
                cr.write(table_name=STOCK_DB_TABLE, record_id=int(move_id), qty_done=float(move_qty_done), confirmed=True)
        # update order state if all lines confirmed
        # not_confirmed_lines = cr.search(query="""
        #     select id from multimove where order_id=%s and confirmed is false
        # """, params=(order_id, ))
        # if not_confirmed_lines and len(not_confirmed_lines) == 0:
        #     cr.write(table_name=ORDER_DB_TABLE, record_id=order_id, state='done')

        new_po_state = 'done'
        if order.get('payment_term') == 'on_delivery':
            new_po_state = 'await_payment'

        cr.write(table_name=ORDER_DB_TABLE, record_id=order_id, state=new_po_state)

        return redirect(url_for('order_page.view_detail', order_id=order_id))

    return render_template(
        template_name_or_list='order/purchase_receive.html',
        order=order,
        moves=lines,
        page_title='Отримання товару'
    )


@purchase_app.route('/purchase/', methods=['GET'])
def view_list():
    return render_template(
        template_name_or_list='order/list.html',
        orders=_list_orders(order_type='purchase'),
        page_title='Закупівлі'
    )


@purchase_app.route('/purchase/create/', methods=['GET', 'POST'])
def view_create():
    order = None
    error = None
    # handle form submit
    if request.method == 'POST':
        if request.form.get('partner_id', False) and request.form.get('incoterm', False) and request.form.get('payment_term', False):
            # create record in DB
            order_id = cr.create(table_name='multiorder', **request.form, type='purchase', )
            return redirect(url_for('order_page.view_detail', order_id=order_id))
        else:
            error = "Invalid data"
        # for errors - save defined data
        order = request.form

    # render tpl
    return render_template(
        template_name_or_list='order/form.html',
        form=order,
        page_title='Ордер на закупівлю',
        partners=_partners_list(),
        incoterms=INCOTERMS,
        payterms=PAYMENT_TERMS,
        error=error,
    )

