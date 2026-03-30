from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from extension  import db
from models import CartItem, OrderItem, Order, Cart
from forms import CheckOutForm

orders = Blueprint('orders', __name__)



# checkout route
@orders.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    form = CheckOutForm()

    cart = db.session.scalars(
        db.select(Cart).where(Cart.user_id == current_user.id)
    ).first()

    if not cart or not cart.items:
        flash(f'{current_user.name}, your cart is empty.', 'danger')
        return redirect(url_for('cart.view_cart'))

    if form.validate_on_submit():

        # Create order
        order = Order(
            user_id=current_user.id,
            total_price=0,
            status='Pending'
        )
        db.session.add(order)
        db.session.flush()

        total = 0

        # Convert cart to order items
        for item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
            )

            total += item.quantity * item.product.price
            db.session.add(order_item)

        # Set total
        order.total_price = total

        # Save form data
        order.name = form.name.data
        order.address = form.address.data
        order.phone = form.phone.data

        # cart
        CartItem.query.filter_by(cart_id=cart.id).delete()

        # Commit
        db.session.commit()

        flash("Order placed successfully!", "success")
        return redirect(url_for('orders.view_orders'))
    # GET request OR invalid form
    return render_template("confirm.html", form=form,
                           cart=Cart.query.filter_by(user_id=current_user.id).scalar())



@orders.route('/view_orders')
@login_required
def view_orders():
    orders = db.session.execute(db.select(OrderItem).where(OrderItem.order_id == current_user.id)).scalars().all()
    if not orders:
        flash('Order not found.', 'danger')
        return redirect(url_for('cart.view_cart'))
    return render_template("orders.html", orders=orders, cart=OrderItem.query.filter_by(order_id=current_user.id).first())

