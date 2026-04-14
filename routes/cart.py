from dns.e164 import query
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from models import Product, Cart, CartItem, Order, OrderItem
from extension import db

cart = Blueprint('cart', __name__)

# To list all items in the shop for customers
@cart.route('/view_all_products')
def view_all_products():
    result = db.session.execute(db.select(Product))
    product = result.scalars().all()
    return render_template('products.html', products=product)

@cart.route('/search')
def search():
    query = request.args.get('q')

    if not query:
        products = []
    else:
        products = Product.query.filter(
            Product.name.ilike(f"%{query}%")
        ).all()

    return render_template(
        'search.html',
        products=products,
        query=query
    )
@cart.route('/special')
def special():
    return render_template('special.html')




# view products detail
@cart.route('/product_detail/<int:product_id>')
def product_detail(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template('product_detail.html', product=product)

# add to cart route
@cart.route('/add_cart/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_cart(product_id):
    # check if user already have cart
    cart = db.session.execute(db.select(Cart).where(Cart.user_id==current_user.id)).scalar()

    # if user does not have we create cart
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

        #  check if product/item already exist in cart
    cart_item = db.session.execute(db.select(CartItem).where(
        CartItem.product_id==product_id,
        CartItem.cart_id==cart.id)).scalar()
    if cart_item:
        #increase quantity
        cart_item.quantity += 1
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=1,
        )
        db.session.add(cart_item)

    db.session.commit()
    flash(f'{cart_item.product.name} added to cart.', 'success')
    return redirect('/cart')

@cart.route("/cart")
@login_required
def view_cart():

    # Get user's cart
    cart = db.session.execute(
        db.select(Cart).where(Cart.user_id == current_user.id)
    ).scalar()

    if not cart or not cart.items:
        return render_template("cart.html", cart=None, total=0)

    total = 0

    # Calculate total
    for item in cart.items:
        total += item.quantity * item.product.price

    return render_template("cart.html", cart=cart, total=total)

@cart.route('/remove_item/<int:item_id>', methods=['GET','POST'])
@login_required
def remove_item(item_id):
    try:
        # Get user's cart
        cart = Cart.query.filter_by(user_id=current_user.id).first()

        if not cart:
            flash("Cart not found", "danger")
            return redirect(url_for('cart.view_cart'))

        # Get item safely (belonging to this cart)
        item_to_remove = CartItem.query.filter_by(
            id=item_id,
            cart_id=cart.id
        ).first()

        if not item_to_remove:
            flash("Item not found", "danger")
            return redirect(url_for('cart.view_cart'))

        # Store name BEFORE delete
        product_name = item_to_remove.product.name

        # Delete
        db.session.delete(item_to_remove)
        db.session.commit()

        flash(f'{product_name} removed from cart.', 'success')

    except Exception as err:
        print(err)
        db.session.rollback()
        flash('Item not removed from cart', 'danger')

    return redirect(url_for('cart.view_cart'))




















