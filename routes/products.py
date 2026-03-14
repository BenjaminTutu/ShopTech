from flask import Flask, render_template, request, Blueprint

from models import Product
from extension import db

products = Blueprint('products', __name__)


# @products.route('/products')
# def products():
#     result = db.session.execute(db.select(Product))
#     product = result.scalars().all()
#     return render_template('products.html', products=product)
#
# @products.route('add_product')
# def add_product():
#
#
#     return render_template('add_product.html')
