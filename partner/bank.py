from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
from . import (
    BANK_DB_TABLE as DB_TABLE,
    PARTNER_DB_TABLE,
)

bank_app = Blueprint('bank_page', __name__, template_folder='templates')


@bank_app.route('/bank/<int:bank_id>/delete/', methods=['GET'])
def view_delete(bank_id):
    bank = cr.read(table_name=DB_TABLE, record_id=bank_id, fields=('partner_id',))
    if cr.unlink(table_name=DB_TABLE, record_id=bank_id):
        return redirect(url_for('partner_page.view_detail', partner_id=bank.get('partner_id')))


@bank_app.route('/bank/', methods=['GET'])
def view_list():
    query = f"""
        select b.id, b.iban, p.id as partner_id, p.name as partner_name 
        from {DB_TABLE} b
        left join {PARTNER_DB_TABLE} p on p.id=b.partner_id 
        order by b.id desc"""
    ibans = cr.search(query)
    return render_template(
        template_name_or_list='bank/bank_list.html',
        ibans=ibans
    )


@bank_app.route('/bank/create/<int:partner_id>/', methods=['GET', 'POST'])
@bank_app.route('/bank/create/', methods=['GET', 'POST'])
def view_create(partner_id: int = None):
    bank = None
    partner = None
    partners = None
    error = None
    if partner_id:
        partner = cr.read('partner', record_id=partner_id, fields=('id', 'name'))
    else:
        partners = cr.search(query=f"""select * from {PARTNER_DB_TABLE}""")

    # handle form submit
    if request.method == 'POST':
        if request.form.get('iban', False) and request.form.get('partner_id', False):
            # create record in DB
            bank_id = cr.create(table_name=DB_TABLE, **request.form)
            return redirect(url_for('partner_page.view_detail', partner_id=request.form.get('partner_id')))
        else:
            error = "Invalid IBAN"
        # for errors - save defined data
        bank = request.form

    # render tpl
    return render_template(
        template_name_or_list='bank/bank_form.html',
        form=bank,
        partner=partner,
        partners=partners,
        error=error,
    )