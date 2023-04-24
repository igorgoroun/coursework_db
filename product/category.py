from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr
import logging
from . import (
    PRODUCT_TYPES
)

_logger = logging.getLogger(__name__)

category_app = Blueprint('category_page', __name__, template_folder='templates')


@category_app.route('/category/<int:category_id>/delete/', methods=['GET'])
def view_delete(category_id):
    if cr.unlink(table_name="category", record_id=category_id):
        return redirect(url_for('category_page.view_list'))


@category_app.route('/category/', methods=['GET'])
def view_list():
    return render_template(
        template_name_or_list='category/list.html',
        categories=_list()
    )


def _list():
    query = f"""
        select c.id, c.name, count(ca.*) as attrs_count, case when count(ca.*)=0 then NULL else 1 end as attrs_sort
        from category c
        left join category_attribute ca on ca.category_id=c.id
        group by c.id, c.name
        order by attrs_sort desc, c.name asc
    """
    return cr.search(query)


@category_app.route('/category/create/', methods=['GET', 'POST'])
def view_create():
    category = None
    error = None
    # handle form submit
    if request.method == 'POST':
        if request.form.get('name', False):
            # create record in DB
            cr.create(table_name='category', **request.form)
            return redirect(url_for('category_page.view_list'))
        else:
            error = "Invalid category Name"
        # for errors - save defined data
        category = request.form

    # render tpl
    return render_template(
        template_name_or_list='category/form.html',
        form=category,
        error=error,
    )


@category_app.route('/category/<int:category_id>', methods=['GET'])
def view_detail(category_id):
    category = cr.read(table_name="category", record_id=category_id, fields=('id', 'name'))
    if not category:
        abort(404)

    applied_query = f"""
        select a.id, a.name 
        from category_attribute ca
        left join attribute a on a.id = ca.attribute_id 
        where ca.category_id=%s
    """
    applied_attrs = cr.search(query=applied_query, params=(category_id, ))
    _logger.info("Applied attrs:", applied_attrs)

    not_applied_query = f"""
        select a.id, a.name
        from "attribute" a
        left join category_attribute ca on ca.attribute_id=a.id and ca.category_id=%s
        where ca.id is null
    """
    not_applied_attrs = cr.search(query=not_applied_query, params=(category_id, ))
    _logger.info("Not Applied attrs:", not_applied_attrs)

    return render_template(
        template_name_or_list='category/detail.html',
        category=category,
        applied_attrs=applied_attrs,
        not_applied_attrs=not_applied_attrs
    )
