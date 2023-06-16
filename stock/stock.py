from flask import Blueprint, render_template, request, url_for, redirect, abort
import db as cr

stock_app = Blueprint('stock_page', __name__, template_folder='templates')


@stock_app.route('/stock/')
def view_stock(order_by='product_id', filter=None):
    pass