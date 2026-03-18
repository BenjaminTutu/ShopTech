from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_user, login_required
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.sql.functions import user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm
from models import User
from extension import db

auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    return render_template('index.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        phone = form.phone.data
        if User.query.filter_by(email=email).first() is not None:
            flash('Email already registered.', 'danger')
        elif db.session.execute(db.select(User).where(User.phone == phone)).scalar_one_or_none():
            flash('Phone Number Already Exist.', 'danger')
            return redirect(url_for('auth.register'))
        else:
            hashed_password = generate_password_hash(
                form.password.data,
                method='pbkdf2:sha256',
                salt_length=8
            )
            try:
                new_user = User(
                    name=form.name.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    password=hashed_password
                )
                db.session.add(new_user)
                db.session.commit()
                flash('You have successfully registered. Please Log In!', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                print(e)

    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = form.email.data
        password = form.password.data
        try:
            result = db.session.execute(db.select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user and check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('auth.home'))
            elif not user:
                flash('Login Unsuccessful. Email Doesn\'t Exist', 'danger')
                return redirect(url_for('auth.login'))
        except MultipleResultsFound as e:
            print(f"Multiple Results Found: {e}")

    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    login_user(user, remember=False)

    return redirect(url_for('auth.home'))

# user profile server side
@auth.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)
