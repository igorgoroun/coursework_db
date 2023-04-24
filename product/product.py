from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
from . import (
    PRODUCT_TYPES
)
from .category import _list as _categories_list
from .brand import _list as _brands_list

product_app = Blueprint('product_page', __name__, template_folder='templates')


@product_app.route('/product/<int:product_id>/delete/', methods=['GET'])
def view_delete(product_id):
    # product = cr.read(table_name="product", record_id=product_id, fields=('partner_id',))
    if cr.unlink(table_name="product", record_id=product_id):
        return redirect(url_for('product_page.view_list'))


@product_app.route('/product/', methods=['GET'])
def view_list():
    return render_template(
        template_name_or_list='product/list.html',
        products=_list()
    )


def _list():
    query = f"""
        select p.id, p.sku, p.model, p.rrp, c.name as category, b.name as brand
        from product p
        left join category c on c.id=p.category_id
        left join brand b on b.id=p.brand_id
        """
    return cr.search(query)


def _search_by_name(product_name):
    query = f"""
        select p.id, p.sku, p.model, p.rrp, c.name as category, b.name as brand
        from product p
        left join category c on c.id=p.category_id
        left join brand b on b.id=p.brand_id
        where p.sku ilike %s or p.model ilike %s
        """
    print(query)
    return cr.search(query, params=(product_name+'%', product_name+'%', ))


@product_app.route('/product/create/', methods=['GET', 'POST'])
def view_create():
    product = None
    error = None
    # handle form submit
    if request.method == 'POST':
        if request.form.get('product_type', False) and request.form.get('model', False) and request.form.get('sku', False) and request.form.get('category_id', False) and request.form.get('brand_id', False):
            # create record in DB
            cr.create(table_name='product', **request.form)
            return redirect(url_for('product_page.view_list'))
        else:
            error = "Невірні дані для продукта"
        # for errors - save defined data
        product = request.form

    # render tpl
    return render_template(
        template_name_or_list='product/form.html',
        form=product,
        error=error,
        product_types=PRODUCT_TYPES,
        categories=_categories_list(),
        brands=_brands_list()
    )


@product_app.route('/product/<int:product_id>', methods=['GET'])
def view_detail(product_id):
    product = cr.read(table_name="product", record_id=product_id, fields=('id', 'sku', 'category_id'))
    if not product:
        abort(404)

    applied_query = f"""
        select pa.category_attribute_id, pa.product_id, pa.value, a.name
        from product_attribute pa
        left JOIN category_attribute ca ON pa.category_attribute_id=ca.id
        LEFT JOIN attribute a ON ca.attribute_id = a.id
        where pa.product_id=%s;
    """
    applied_attrs = cr.search(query=applied_query, params=(product_id, ))

    not_applied_query = f"""
        select ca.id, a.name, pa.category_attribute_id, pa.product_id
        from category_attribute ca
        left join attribute a on a.id=ca.attribute_id
        left join product_attribute pa on pa.category_attribute_id=ca.id and pa.product_id=%s
        where ca.category_id=%s and product_id is null
    """
    not_applied_attrs = cr.search(query=not_applied_query, params=(product_id, product.get('category_id'), ))

    return render_template(
        template_name_or_list='product/detail.html',
        product=product,
        applied_attrs=applied_attrs,
        not_applied_attrs=not_applied_attrs
    )