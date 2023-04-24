from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
from . import (
    PRODUCT_TYPES
)

attribute_app = Blueprint('attribute_page', __name__, template_folder='templates')


@attribute_app.route('/attribute/<int:attribute_id>/delete/', methods=['GET'])
def view_delete(attribute_id):
    if cr.unlink(table_name="attribute", record_id=attribute_id):
        return redirect(url_for('attribute_page.view_list'))


@attribute_app.route('/attribute/', methods=['GET'])
def view_list():
    query = f"""
        select * from attribute
        order by name"""
    attributes = cr.search(query)
    return render_template(
        template_name_or_list='attribute/list.html',
        attributes=attributes
    )


@attribute_app.route('/attribute/create/', methods=['GET', 'POST'])
def view_create():
    attribute = None
    error = None
    # handle form submit
    if request.method == 'POST':
        if request.form.get('name', False):
            # create record in DB
            cr.create(table_name='attribute', **request.form)
            return redirect(url_for('attribute_page.view_list'))
        else:
            error = "Invalid attribute Name"
        # for errors - save defined data
        attribute = request.form

    # render tpl
    return render_template(
        template_name_or_list='attribute/form.html',
        form=attribute,
        error=error,
    )


@attribute_app.route('/attribute/category/apply/<int:attribute_id>/<int:category_id>/', methods=['GET'])
def apply_to_category(attribute_id, category_id):
    cr.create(table_name='category_attribute', attribute_id=attribute_id, category_id=category_id)
    return redirect(url_for('category_page.view_detail', category_id=category_id))


@attribute_app.route('/attribute/category/remove/<int:attribute_id>/<int:category_id>/', methods=['GET'])
def remove_from_category(attribute_id, category_id):
    del_query = """delete from category_attribute 
        where 
            category_id=%s 
            and attribute_id=%s
    """
    cr.execute(del_query, [category_id, attribute_id])
    return redirect(url_for('category_page.view_detail', category_id=category_id))


@attribute_app.route('/attribute/product/apply/<int:product_id>/<int:category_attribute_id>/', methods=['POST'])
def apply_to_product(product_id, category_attribute_id):
    if request.form.get('value', False):
        # create record in DB
        cr.create(table_name='product_attribute', return_id=False, product_id=product_id, category_attribute_id=category_attribute_id,
                  value=request.form.get('value'))
    return redirect(url_for('product_page.view_detail', product_id=product_id))


@attribute_app.route('/attribute/product/remove/<int:product_id>/<int:category_attribute_id>/', methods=['GET'])
def remove_from_product(product_id, category_attribute_id):
    del_query = """
        delete from product_attribute 
        where product_id=%s and category_attribute_id=%s
    """
    cr.execute(del_query, [product_id, category_attribute_id])
    return redirect(url_for('product_page.view_detail', product_id=product_id))
