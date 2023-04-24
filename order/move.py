from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr

move_app = Blueprint('move_page', __name__, template_folder='templates')


@move_app.route('/move/<int:move_id>/delete/', methods=['GET'])
def view_delete(move_id):
    if cr.unlink(table_name="multimove", record_id=move_id):
        return redirect(url_for('move_page.view_list'))


@move_app.route('/move/create/<int:order_id>/', methods=['POST'])
def add_to_order(order_id):
    order = cr.read('multiorder', record_id=order_id, fields=('id', 'type'))
    if request.form.get('product_id', False) and request.form.get('qty_draft', False) and request.form.get('unit_price'):
        cr.create('multimove', return_id=False, **request.form, order_id=order_id, sign=1 if order.get('type') == 'purchase' else -1, )
    return redirect(url_for('order_page.view_detail', order_id=order_id))


def _list_for_order(order_id):
    query = f"""
        select
            m.id, m.product_id, m.unit_price,
            m.qty_draft, m.qty_done, m.confirmed, 
            p.sku, p.model, p.rrp, 
            c.name as category, b.name as brand,
            m.qty_draft * m.unit_price as amount
        from multimove m
        left join product p on p.id = m.product_id
        left join category c on c.id=p.category_id
        left join brand b on b.id=p.brand_id
        where m.order_id=%s
        """
    return cr.search(query, params=(order_id, ))
