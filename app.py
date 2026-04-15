from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from extension import db
from flask_mail import Mail

from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

@event.listens_for(Engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

db.init_app(app)

Bootstrap5(app)

migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL')

mail = Mail(app)

# Configuring file path
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "images", "products")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# initializing login_manager
login_manager = LoginManager()
login_manager.init_app(app)

# Creating user loader
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Creating DB models
from models import User, Cart

from  routes.auth import auth
from routes.admin import admins
from routes.cart import cart
from routes.orders import orders

# connecting blueprints with app
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(admins, url_prefix='/')
app.register_blueprint(cart, url_prefix='/')
app.register_blueprint(orders, url_prefix='/')


# create context processor for cart counts
@app.context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()

        if cart and cart.items:
            count = sum(item.quantity for item in cart.items)
        else:
            count = 0
    else:
        count = 0

    return dict(cart_count=count)

# from command import create_admin
# app.cli.add_command(create_admin)


@app.route('/setup-admin-<string:token>', methods=['GET'])
def setup_admin(token):
    from models import User
    from werkzeug.security import generate_password_hash

    secret_token = os.getenv("ADMIN_SETUP_TOKEN")

    if token != secret_token:
        return "Unauthorized", 403

    admin = User.query.filter_by(email=os.getenv("ADMIN_EMAIL")).first()
    if admin:
        return "Admin already exists!", 200

    admin = User(
        name="Admin",
        email=os.getenv("ADMIN_EMAIL"),
        phone=os.getenv("ADMIN_PHONE", "0000000000"),
        password=generate_password_hash(os.getenv("ADMIN_PASSWORD")),
        role="admin"
    )
    db.session.add(admin)
    db.session.commit()
    return "Admin created successfully!", 200


if __name__ == '__main__':
    app.run(debug=True)


