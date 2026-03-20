import os
from functools import wraps
from os import abort

from flask import render_template, Blueprint, flash, current_app
from flask_login import  current_user
from werkzeug.utils import secure_filename, redirect

from forms import ProductForm, UpdateProductForm

from models import Product, User
from extension import db

admins = Blueprint('admins', __name__)


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
@admins.route('/admin')
@admin_required
def admin():

    return render_template('admin_dashboard.html')


# Add product route
@admins.route('/add_product', methods=['GET', 'POST'])
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
        return redirect('admins.admin')

    return render_template('add_product.html', form=form)

# Product deletion route
@admins.route('/delete_product<int:product_id>')
@admin_required
def delete_product(product_id):
    product_to_delete = db.get_or_404(Product, product_id)
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect('admins.admin')



# edit products route
@admins.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    # getting product by id
    product = db.get_or_404(Product, product_id)

    # pre-populating form entry field with selected products
    form = UpdateProductForm(obj=product)

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
                return redirect('admin')

            # raises exception if there's error while committing to db
            except Exception as e:
                print(e)
                flash('Product not updated.', 'danger')

    return render_template('edit_product.html', form=form, product=product)


# Route for Shop Admin to view all products
@admins.route('/shop_items')
@admin_required
def shop_items():
    result = db.session.execute(db.select(Product))
    product = result.scalars().all()
    return render_template('shop_items.html', products=product)


# Route for Shop Admin to view all customers details
@admins.route('/view_all_customers')
@admin_required
def view_all_customers():
    result = db.session.execute(db.select(User))
    user = result.scalars().all()
    return render_template('customers.html', user=user, cart=user.cart, orders=user.orders)



#  fopr viewing a particular customer details
@admins.route('/view_customer<int:user_id>', methods=['GET', 'POST'])
@admin_required
def view_customer(user_id):
    result = db.get_or_404(User, user_id)
    return render_template('profile.html', user=result)

@admins.route('/delete_customer<int:user_id>', methods=['GET', 'POST'])
@admin_required
def delete_customer(user_id):
    customer_to_delete = db.get_or_404(User, user_id)
    db.session.delete(customer_to_delete)
    db.session.commit()
    return redirect('admins.admin')






