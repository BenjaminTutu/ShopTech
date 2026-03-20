from flask import Blueprint, render_template
from models import Product
from extension import db

cart = Blueprint('cart', __name__)

# To list all items in the shop for customers in the product section of the website
@cart.route('/view_all_products')
def view_all_products():
    result = db.session.execute(db.select(Product))
    product = result.scalars().all()
    return render_template('products.html', products=product)