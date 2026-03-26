from flask import Blueprint, render_template, request, flash, redirect
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

# view products detail
@cart.route('/product_detail/<int:product_id>')
def product_detail(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template('product_detail.html', product=product)

# add to cart route
@cart.route('/add_cart/<int:product_id>', methods=['GET', 'POST'])
def add_cart(product_id):
    # check if user already have cart
    cart = db.session.execute(db.select(Cart).where(Cart.user_id==current_user.id)).first()

    # if user does not have we create cart
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

        #  check if product/item already exist in cart
        cart_item = db.session.execute(db.select(CartItem).where(
            CartItem.product_id==product_id,
            CartItem.cart_id==cart.id)).first()
        if cart_item:
            #increase quantity
            cart_item.quantity += 1
            db
        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=1,
            )
        db.session.commit()
        flash(f'{product_id.name} added to cart.', 'success')

# remove cart_item
@cart.route('/remove_cart/<int:product_id>', methods=['GET', 'POST'])
def remove_cart(product_id):
    try:
        cart_item = db.session.execute(db.select(CartItem).where(CartItem.product_id==product_id)).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            flash(f'{product_id.name} removed from cart.', 'success')
    except Exception as err:
        db.session.rollback()
        flash(f'{err}', 'danger')


# checkout route
@cart.route('/checkout', methods=['GET', 'POST'])
def checkout():
    try:
        cart = db.session.execute(db.select(Cart).where(Cart.user_id==current_user.id)).first()
        if not cart:
            flash(f'{current_user.id} has no cart.', 'danger')
            return redirect('/cart')

        # create new order
        order = Order(
            user_id=current_user.id,
            total_price=cart.total_price,
            status='status'
        )
        db.session.add(order)
        db.session.commit()

        total = 0

#         cart_items to order_items
        for item in cart.items:
            product = item.product
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                price=product.price
            )

            total += item.quantity * product.price
            db.session.add(order_item)

        order.total_price = total
        db.session.commit()

        db.session.execute(db.delete(CartItem).where(CartItem.cart_id==cart.id))
        db.session.commit()

        flash('Your order has been placed.', 'success')
        return redirect('/orders')


    except Exception as err:
        print(err)
        db.session.rollback()



















