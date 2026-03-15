import os
from functools import wraps
from os import abort

from flask import Flask, render_template, request, Blueprint
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename, redirect

from forms import ProductForm

from models import Product
from extension import db

products = Blueprint('products', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@products.route('/admin')
@admin_required
def admin():
    results = db.session.execute(db.select(Product))
    product = results.scalars().all()
    return render_template('admin.html', products=product)



@products.route('/products_view')
def products_view():
    result = db.session.execute(db.select(Product))
    product = result.scalars().all()
    return render_template('products.html', products=product)

@products.route('/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        image_file = form.image.data
        filename = secure_filename(image_file.filename)

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image=image_path,
            stock=form.stock.data,
        )
        db.session.add(product)
        db.session.commit()
        return redirect('products.admin')

    return render_template('add_product.html', form=form)

@products.route('/delete_product<int:product_id>')
@admin_required
def delete_product(product_id):
    product_to_delete = db.session.get_or_404(Product, product_id)
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect('products.admin')

@products.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    form = ProductForm()
