import os
from functools import wraps
from os import abort

from flask import render_template, Blueprint, flash, current_app, url_for, redirect, request
from flask_login import  current_user
from werkzeug.utils import secure_filename, redirect

from forms import ProductForm, UpdateProductForm, OrderStatus

from models import Product, User, Order
from extension import db

admins = Blueprint('admins', __name__)


# File for all admin functions


# Admin decoration for only admin access to certain features
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # must be logged in for access
        if not current_user.is_authenticated:
            abort()
        #  must have an admin role in db
        if current_user.role != "admin":
            abort()
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
            previous_price=form.previous_price.data,
            image=filename,
            stock=form.stock.data,
            rating=form.rating.data,
        )
        db.session.add(product)
        db.session.commit()
        flash('Product successfully added!', 'success')
        return redirect('/admin')

    return render_template('add_product.html', form=form)

# Product deletion route
@admins.route('/delete_product<int:product_id>')
@admin_required
def delete_product(product_id):
    product_to_delete = db.get_or_404(Product, product_id)
    db.session.delete(product_to_delete)
    db.session.commit()
    flash("Item successfully deleted!", "success")
    return redirect('/admin')



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
        product.previous_price = form.previous_price.data
        product.stock = form.stock.data
        product.rating = form.rating.data

        # updating image if new image is uploaded, if not, saves product info without img
        image_file = form.image.data
        if image_file and hasattr(image_file, 'filename') and image_file.filename != '':

            # deleting existing image_file
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image)
            if os.path.exists(old_path):
                os.remove(old_path)

            # saving new image_file if exist
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

        #     otherwise maintain old image
        else:
            filename = product.image

        product.image = filename
        # saves product info to db if no error
        try:
            db.session.add(product)
            db.session.commit()
            flash('Product successfully updated!', 'success')
            return redirect('/admin')

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
    return render_template('customers.html', user=user)



#  for viewing a particular customer details including cart, oder history
@admins.route('/view_customer/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def view_customer(user_id):
    user = db.get_or_404(User, user_id)
    return render_template('profile.html', user=user, cart=user.cart, orders=user.orders)

# delete customer
@admins.route('/delete_customer/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def delete_customer(user_id):
    customer_to_delete = db.get_or_404(User, user_id)
    db.session.delete(customer_to_delete)
    db.session.commit()
    flash("Customer successfully deleted!", "success")
    return redirect('/admin')

@admins.route('/admin_orders')
@admin_required
def admin_orders():
    order = Order.query.order_by(Order.id.desc()).all()
    return render_template('orders.html', order=order)


@admins.route("/update_order/<int:order_id>", methods=["GET", "POST"])
@admin_required
def update_order(order_id):
    order = db.get_or_404(Order, order_id)
    form =OrderStatus()
    if form.validate_on_submit():
        order.status = form.status.data
        db.session.commit()
        flash("Order updated!", "success")
        return redirect(url_for("admins.admin_orders"))

    return render_template('update_order.html', order=order, form=form)


@admins.route("/delete_order/<int:order_id>", methods=["GET", "POST"])
@admin_required
def delete_order(order_id):
    order_to_delete = db.get_or_404(Order, order_id)
    db.session.delete(order_to_delete)
    db.session.commit()
    flash("Order successfully deleted!", "success")
    return redirect('orders.admin_orders')




