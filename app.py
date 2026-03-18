from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from extension import db


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

db.init_app(app)

Bootstrap5(app)

migrate = Migrate(app, db)

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
from models import User, Product, Cart, CartItem, Order, OrderItem

from  routes.auth import auth
from routes.products import products

# connecting blueprints with app
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(products, url_prefix='/')









if __name__ == '__main__':
    app.run(debug=True)


