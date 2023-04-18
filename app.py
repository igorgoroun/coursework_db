from flask import Flask, g, render_template
from psycopg2 import connect
from partner.partner import partner_page
from partner.bank import bank_app
from partner.contact import contact_page

app = Flask(__name__)
app.register_blueprint(partner_page)
app.register_blueprint(bank_app)
app.register_blueprint(contact_page)


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
