from flask import Blueprint, render_template, request, url_for, redirect, abort
from db import create, read, search, write, unlink
from . import (
    PARTNER_DB_TABLE as DB_TABLE,
    BANK_DB_TABLE,
    CONTACT_DB_TABLE,
    INCOTERMS,
    PAYMENT_TERMS
)

partner_page = Blueprint('partner_page', __name__, template_folder='templates')


@partner_page.route('/partner/', methods=['GET'])
def view_list():
    query = f"""
        with 
        partner_contacts as (select partner_id as id, COUNT(*) as cnt from {CONTACT_DB_TABLE} group by partner_id),
        partner_banks as (select partner_id as id, count(*) as cnt from {BANK_DB_TABLE} group by partner_id)
        select p.*, c.cnt as contacts_count, b.cnt as banks_count from {DB_TABLE} p 
        left join partner_contacts c on c.id=p.id
        left join partner_banks b on b.id=p.id
    """
    partners = search(query)
    return render_template(
        template_name_or_list='partner/partner_list.html',
        partners=partners
    )


@partner_page.route('/partner/<int:partner_id>', methods=['GET'])
def view_detail(partner_id):
    partner = read(table_name=DB_TABLE, record_id=partner_id, fields=('id', 'name', 'default_incoterm', 'default_payment_term'))
    if not partner:
        abort(404)

    contacts_query = f"""select * from {CONTACT_DB_TABLE} where partner_id=%s"""
    contacts = search(query=contacts_query, params=(partner_id, ))

    banks_query = f"""select * from {BANK_DB_TABLE} where partner_id=%s"""
    banks = search(query=banks_query, params=(partner_id, ))

    return render_template(
        template_name_or_list='partner/partner_detail.html',
        partner=partner,
        contacts=contacts,
        banks=banks
    )


@partner_page.route('/partner/create/', methods=['GET', 'POST'])
def view_create():
    form_data = None
    error = None
    if request.method == 'POST':
        if request.form.get('name', False):
            # create record in DB
            partner_id = create(table_name=DB_TABLE, **request.form)
            return redirect(url_for('.view_detail', partner_id=partner_id))
        else:
            error = "Invalid counterparty name"
        # for errors - save defined data
        form_data = request.form
    # render tpl
    return render_template(
        template_name_or_list='partner/partner_form.html',
        form=form_data,
        error=error,
        incoterms=INCOTERMS,
        payment_terms=PAYMENT_TERMS
    )


@partner_page.route('/partner/<partner_id>/modify/', methods=['POST', 'GET'])
def view_modify(partner_id):
    partner = read(table_name=DB_TABLE, record_id=partner_id, fields=('name', 'default_incoterm', 'default_payment_term'))
    if not partner:
        abort(404)
    error = None
    if request.method == 'POST':
        if request.form.get('name', False):
            write(table_name=DB_TABLE, record_id=partner_id, **request.form)
            return redirect(url_for('.view_detail', partner_id=partner_id))
        else:
            error = "Counterparty name cannot be empty"
        partner = request.form
    return render_template(
        template_name_or_list='partner/partner_form.html',
        form=partner,
        error=error,
        incoterms=INCOTERMS,
        payment_terms=PAYMENT_TERMS
    )


@partner_page.route('/partner/<partner_id>/delete/', methods=['GET'])
def view_delete(partner_id):
    if unlink(table_name=DB_TABLE, record_id=partner_id):
        return redirect(url_for('.view_list'))
