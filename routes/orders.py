import os
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
    from app import mail, app
    from flask_mail import Message
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
            product = item.product
            if product.stock < item.quantity:
                flash(f'Not enough stock for {product.name}', 'danger')
                return redirect(url_for('cart.view_cart'))
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
            )
            product.stock -= item.quantity

            total += item.quantity * item.product.price
            db.session.add(order_item)

        # Set total
        order.total_price = total

        # Save form data
        order.name = form.name.data
        order.address = form.address.data
        order.phone = form.phone.data

        # delete cart
        CartItem.query.filter_by(cart_id=cart.id).delete()

        # Commit
        db.session.commit()
        flash("Order placed successfully!", "success")

        #send oder confirmation message to customer
        msg = Message(
            subject="Your Order has been created!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[current_user.email]
        )

        msg.body = f"""
        Hello {order.name}!
        Your order #{order.id} has been created.
        Total: {order.total_price}.
        Thank you for shopping with ShopTech
        """

        try:
            mail.send(msg)
        except Exception as e:
            print("Email failed:", e)
        return redirect(url_for('orders.view_orders'))

    # set total price to display in order confirmation
    total = 0
    for item in cart.items:
        total += item.quantity * item.product.price

    # GET request OR invalid form
    return render_template("confirm.html", form=form,
                           cart=Cart.query.filter_by(user_id=current_user.id).scalar(), total=total)

@orders.route("/view_orders")
@login_required
def view_orders():
    order = db.session.execute(db.select(Order).where(Order.user_id == current_user.id).order_by(Order.id.desc()))
    order = order.scalars().all()

    return render_template("orders.html", order=order)
