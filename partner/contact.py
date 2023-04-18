from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
from . import (
    CONTACT_DB_TABLE as DB_TABLE,
    PARTNER_DB_TABLE,
    CONTACT_TYPES
)

contact_page = Blueprint('contact_page', __name__, template_folder='templates')


@contact_page.route('/contact/<int:contact_id>/delete/', methods=['GET'])
def view_delete(contact_id):
    bank = cr.read(table_name=DB_TABLE, record_id=contact_id, fields=('partner_id',))
    if cr.unlink(table_name=DB_TABLE, record_id=contact_id):
        return redirect(url_for('partner_page.view_detail', partner_id=bank.get('partner_id')))


@contact_page.route('/contact/', methods=['GET'])
def view_list():
    query = f"""
        select c.id, c.name, c.type, c.address, c.phone, p.id as partner_id, p.name as partner_name 
        from {DB_TABLE} c
        left join {PARTNER_DB_TABLE} p on p.id=c.partner_id 
        order by c.id desc"""
    contacts = cr.search(query)
    return render_template(
        template_name_or_list='contact/contact_list.html',
        contacts=contacts
    )


@contact_page.route('/contact/create/<int:partner_id>/', methods=['GET', 'POST'])
@contact_page.route('/contact/create/', methods=['GET', 'POST'])
def view_create(partner_id: int = None):
    contact = None
    partner = None
    partners = None
    error = None
    if partner_id:
        partner = cr.read('partner', record_id=partner_id, fields=('id', 'name'))
    else:
        partners = cr.search(query=f"""select * from {PARTNER_DB_TABLE}""")

    # handle form submit
    if request.method == 'POST':
        if request.form.get('type', False) and request.form.get('partner_id', False):
            # create record in DB
            contact_id = cr.create(table_name=DB_TABLE, **request.form)
            return redirect(url_for('partner_page.view_detail', partner_id=request.form.get('partner_id')))
        else:
            error = "Invalid contact type"
        # for errors - save defined data
        contact = request.form

    # render tpl
    return render_template(
        template_name_or_list='contact/contact_form.html',
        form=contact,
        types=CONTACT_TYPES,
        partner=partner,
        partners=partners,
        error=error,
    )