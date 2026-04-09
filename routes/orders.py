import json
import os
from flask import Blueprint, flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from extension  import db
from models import CartItem, OrderItem, Order, Cart
from forms import CheckOutForm
import requests
import uuid
import hashlib
import hmac

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
        flash("Order placed successfully! Please proceed to make payment", "success")

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
        Please go ahead and make payment for delivery.
        -------
        Thank you for shopping with ShopTech
        -------
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


# Paystack payment integration
#paystack api call route
@orders.route("/pay/<int:order_id>", methods=["POST","GET"])
@login_required
def pay(order_id):
    order = Order.query.get_or_404(order_id)

    if order.status == 'Paid':
        flash("Order already paid!", "info")
        return redirect(url_for('orders.view_orders'))

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}",
        "Content-Type": "application/json"
    }

    # creating reference id & commit to db
    reference = f"Order-{order.id}-{uuid.uuid4().hex}"
    order.payment_reference = reference
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        flash("Something went wrong!", "danger")
        db.session.rollback()

    data = {
        "email": current_user.email,
        "amount": int(order.total_price * 100),
        "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
        "reference": reference,
        "callback_url": url_for('orders.verify_payment', _external=True),
        "label": f"Payment for (Order #{order.id})"
    }
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    print(response_data)

    if response_data.get('status'):
        return redirect(response_data["data"]["authorization_url"])

    flash("Payment Failed To Processed!", "danger")
    return redirect(url_for('orders.view_orders'))

# paystack-payment verifier
@orders.route("/verify_payment/")
@login_required
def verify_payment():
    reference = request.args.get('reference')
    print("Reference from WHK",reference)

    order = Order.query.filter_by(payment_reference=reference).first()
    if order is None:
        flash("Oder not found!", "danger")
        return redirect(url_for('orders.view_orders'))

    if order.status == 'Paid':
        flash(f"Payment Successful! Ref:ORDER #{order}." "success")
        return redirect(url_for('orders.view_orders'))
    else:
        flash("Payment is being processed!", "danger")

    return redirect(url_for('orders.view_orders'))


# creating webhook for backend communication
@orders.route("/webhook", methods=["POST"])
def webhook():
    print("WEBHOOK HIT")
    payload = request.get_data()
    print(payload)

    signature = request.headers.get('x-paystack-signature')
    print(signature)
    secret = os.getenv('PAYSTACK_SECRET_KEY').encode('utf-8')

    hash = hmac.new(secret, payload, hashlib.sha512).hexdigest()
    if hash != signature:
        return "Invalid signature!", 400

    data = json.loads(payload)
    print(data)

    if data['event'] == 'charge.success':
        reference = data['data']['reference']

        order = Order.query.filter_by(payment_reference=reference).first()

        if order and order.status != 'Paid':
            order.status = 'Paid'
            try:
                db.session.commit()
            except Exception as e:
                print(e)
                db.session.rollback()

    return 'Webhook Received', 200



@orders.route("/cancel_order/<int:order_id>", methods=["GET", "POST"])
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status == 'Cancelled':
        flash("Order already canceled!", "danger")
        return redirect(url_for('orders.view_orders'))
    order.status = 'Cancelled'
    db.session.commit()
    flash("Order canceled successfully!", "success")
    return redirect(url_for('orders.view_orders'))






