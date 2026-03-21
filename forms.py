from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, IntegerField, FloatField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, length, NumberRange


class RegisterForm(FlaskForm):
    name = StringField('Username', render_kw={"placeholder": "Enter your username",}, validators=[DataRequired(), length(min=4, max=25)])
    email = EmailField('Email', render_kw={"placeholder": "Enter your email"}, validators=[DataRequired(), Email(), length(max=50)])
    phone = StringField('Phone', render_kw={"placeholder": "Phone"}, validators=[DataRequired()])
    password = PasswordField('Password', render_kw={"placeholder": "Enter your password"}, validators=[DataRequired(), length(min=8)])
    password2 = PasswordField('Confirm Password', render_kw={"placeholder": "Confirm your password"}, validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register', render_kw={"class": "btn btn-success"})

class LoginForm(FlaskForm):
    email = EmailField('Email', render_kw={"placeholder": "Enter your email"}, validators=[DataRequired()])
    password = PasswordField('Password', render_kw={"placeholder": "Enter your password"}, validators=[DataRequired()])
    remember_me = BooleanField('Remember Me', render_kw={"class": "form-check-input"})
    submit = SubmitField('Login', render_kw={"class": "btn btn-success"})

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('', render_kw={"placeholder": "Enter your old password"}, validators=[DataRequired()])
    password = PasswordField('', render_kw={"placeholder": "Enter your new password"}, validators=[DataRequired()])
    password2 = PasswordField('', render_kw={"placeholder": "Confirm your new password"}, validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password', render_kw={"class": "btn btn-success"})

class CheckOutForm(FlaskForm):
    name = StringField('Name', render_kw={"placeholder": "Enter your name"}, validators=[DataRequired()])
    address = StringField('Address', render_kw={"placeholder": "Enter your address"}, validators=[DataRequired()])
    city = StringField('City', render_kw={"placeholder": "City"},validators=[DataRequired()])
    postcode = StringField('Postcode', render_kw={"placeholder": "Postcode"},validators=[DataRequired()])
    country = StringField('Country', render_kw={"placeholder": "Country"},validators=[DataRequired()])
    phone = StringField('Phone', render_kw={"placeholder": "Enter your phone number"},validators=[DataRequired()])
    email = StringField('Email', render_kw={"placeholder": "Enter your email"},validators=[DataRequired(), Email()])
    submit = SubmitField('Confirm Order', render_kw={"class": "btn btn-primary"})


# /add_product form
class ProductForm(FlaskForm):
    name = StringField("Product Name", render_kw={'placeholder': 'Product name'}, validators=[DataRequired()])
    price = FloatField("Price", render_kw={'placeholder': 'Product price'} ,validators=[DataRequired()])

    # adding migration previous_price change from db to Product form
    previous_price = FloatField("Previous Price", render_kw={'placeholder': 'Previous price'}, validators=[DataRequired()])

    stock = IntegerField("Stock", render_kw={'placeholder': 'Available stock'}, validators=[DataRequired()])
    description = TextAreaField("Description", render_kw={'placeholder': 'Product description'})
    image = FileField("Product Image", render_kw={'placeholder': 'Product image'}, validators=[DataRequired()])

    # adding Migration rating change from db to Product form
    rating = FloatField("Rating", render_kw={'placeholder': 'Rating'}, validators=[NumberRange(min=0, max=5)])

    submit = SubmitField("Add Product", render_kw={"class": "btn btn-primary"})




# /edit_product form
class UpdateProductForm(FlaskForm):
    name = StringField("Product Name", render_kw={'placeholder': 'Product name'}, validators=[DataRequired()])
    price = FloatField("Price", render_kw={'placeholder': 'Product price'} ,validators=[DataRequired()])

    # adding migration previous_price  chanage from db to Product form
    previous_price = FloatField("Previous Price", render_kw={'placeholder': 'Previous price'},validators=[DataRequired()])

    stock = IntegerField("Stock", render_kw={'placeholder': 'Available stock'}, validators=[DataRequired()])
    description = TextAreaField("Description", render_kw={'placeholder': 'Product description'})
    image = FileField("Product Image")

    # adding  migration  rating change from db to Product form
    rating = FloatField("Rating", render_kw={'placeholder': 'Rating'}, validators=[NumberRange(min=0, max=5)])
    submit = SubmitField("Update Product", render_kw={"class": "btn btn-primary"})

class OrderForm(FlaskForm):
    pass