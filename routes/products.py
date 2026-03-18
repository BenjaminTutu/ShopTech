import os
from functools import wraps
from os import abort

from flask import render_template, Blueprint, flash, current_app
from flask_login import  current_user
from werkzeug.utils import secure_filename, redirect

from forms import ProductForm

from models import Product
from extension import db

products = Blueprint('products', __name__)


# Admin decoration for only admin access to certain features
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # must be logged in for access
        if not current_user.is_authenticated:
            abort(401)

        #  must have an admin role in db
        if current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# Admin Dashboard Route
@products.route('/admin')
@admin_required
def admin():

    return render_template('admin.html')


# view all products
@products.route('/products_view')
def products_view():
    result = db.session.execute(db.select(Product))
    product = result.scalars().all()
    return render_template('products.html', products=product)

# Add product route
@products.route('/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():

        # saving image path
        image_file = form.image.data
        filename = secure_filename(image_file.filename)

        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)

        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image=filename,
            stock=form.stock.data,
        )
        db.session.add(product)
        db.session.commit()
        flash('Product successfully added!', 'success')
        return redirect('products.admin')

    return render_template('add_product.html', form=form)

# Product deletion route
@products.route('/delete_product<int:product_id>')
@admin_required
def delete_product(product_id):
    product_to_delete = db.session.get_or_404(Product, product_id)
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect('products.admin')



# edit products route
@products.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    # getting product by id
    product = db.get_or_404(Product, product_id)

    # pre-populating form entry field with selected products
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data

        # updating image if new image is uploaded, if not, saves product info without img
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            product.image = filename

            # saves product info to db if no error
            try:
                db.session.add(product)
                db.session.commit()
                flash('Product successfully updated!', 'success')
                return redirect('products.admin')

            # raises exception if there's error while committing to db
            except Exception as e:
                print(e)
                flash('Product not updated.', 'danger')

    return render_template('edit_product.html', form=form, product=product)









