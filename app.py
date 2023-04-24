from flask import Flask, g, render_template
# from psycopg2 import connect
from partner.partner import partner_page
from partner.bank import bank_app
from partner.contact import contact_page
from product.brand import brand_app
from product.attribute import attribute_app
from product.category import category_app
from product.product import product_app
from order.purchase import purchase_app
from order.order import order_app
from order.move import move_app

app = Flask(__name__)
app.register_blueprint(partner_page)
app.register_blueprint(bank_app)
app.register_blueprint(contact_page)
app.register_blueprint(brand_app)
app.register_blueprint(attribute_app)
app.register_blueprint(category_app)
app.register_blueprint(product_app)
app.register_blueprint(order_app)
app.register_blueprint(move_app)
app.register_blueprint(purchase_app)


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/')
def dashboard():
    return render_template(template_name_or_list='layout.html')


if __name__ == '__main__':
    app.run()
