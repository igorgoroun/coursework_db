from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
from .order import _list_orders, _get_detail
from partner import (
    PAYMENT_TERMS,
    INCOTERMS
)
from partner.partner import _list as _partners_list

purchase_app = Blueprint('purchase_page', __name__, template_folder='templates')


@purchase_app.route('/purchase/', methods=['GET'])
def view_list():
    return render_template(
        template_name_or_list='order/list.html',
        orders=_list_orders(order_type='purchase'),
        page_title='Закупки'
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

