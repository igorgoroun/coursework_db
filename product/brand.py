from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
from . import (
    PRODUCT_TYPES
)

brand_app = Blueprint('brand_page', __name__, template_folder='templates')


@brand_app.route('/brand/<int:brand_id>/delete/', methods=['GET'])
def view_delete(brand_id):
    # brand = cr.read(table_name="brand", record_id=brand_id, fields=('partner_id',))
    if cr.unlink(table_name="brand", record_id=brand_id):
        return redirect(url_for('brand_page.view_list'))


@brand_app.route('/brand/', methods=['GET'])
def view_list():
    return render_template(
        template_name_or_list='brand/brand_list.html',
        brands=_list()
    )


def _list():
    query = f"""
            select b.id, b.name 
            from brand b
            order by b.name"""
    return cr.search(query)


@brand_app.route('/brand/create/', methods=['GET', 'POST'])
def view_create():
    brand = None
    error = None
    # handle form submit
    if request.method == 'POST':
        if request.form.get('name', False):
            # create record in DB
            cr.create(table_name='brand', **request.form)
            return redirect(url_for('brand_page.view_list'))
        else:
            error = "Invalid Brand Name"
        # for errors - save defined data
        brand = request.form

    # render tpl
    return render_template(
        template_name_or_list='brand/brand_form.html',
        form=brand,
        error=error,
    )