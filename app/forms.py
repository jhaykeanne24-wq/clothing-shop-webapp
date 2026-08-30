from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from app.models import User

# Registration Form with validation
class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=80, message='Username must be 3-80 characters')])
    email = EmailField('Email', 
                      validators=[DataRequired(), Email(message='Invalid email address')])
    password = PasswordField('Password', 
                            validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters')])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or login.')

# Login Form
class LoginForm(FlaskForm):
    """User login form"""
    email = EmailField('Email', 
                      validators=[DataRequired(), Email(message='Invalid email address')])
    password = PasswordField('Password', 
                            validators=[DataRequired()])

# Profile Update Form
class ProfileUpdateForm(FlaskForm):
    """User profile update form"""
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=80)])
    email = EmailField('Email', 
                      validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', 
                       validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', 
                           validators=[Optional(), Length(max=255)])
    city = StringField('City', 
                      validators=[Optional(), Length(max=80)])
    postal_code = StringField('Postal Code', 
                             validators=[Optional(), Length(max=10)])
    country = StringField('Country', 
                         validators=[Optional(), Length(max=80)])

# Product Form (for admin CRUD)
class ProductForm(FlaskForm):
    """Product creation and update form"""
    name = StringField('Product Name', 
                      validators=[DataRequired(), Length(min=3, max=150)])
    description = TextAreaField('Description', 
                               validators=[Optional()])
    category = SelectField('Category', 
                          choices=[('shirts', 'Shirts'),
                                  ('pants', 'Pants'),
                                  ('dresses', 'Dresses'),
                                  ('jackets', 'Jackets'),
                                  ('shoes', 'Shoes'),
                                  ('accessories', 'Accessories')],
                          validators=[DataRequired()])
    price = DecimalField('Price (USD)', 
                        validators=[DataRequired(), NumberRange(min=0.01)])
    cost_price = DecimalField('Cost Price (USD)', 
                             validators=[Optional(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock Quantity', 
                                 validators=[DataRequired(), NumberRange(min=0)])
    size_options = StringField('Size Options (comma-separated)', 
                              validators=[Optional()],
                              default='XS,S,M,L,XL,XXL')
    color_options = StringField('Color Options (comma-separated)', 
                               validators=[Optional()])

# Review Form
class ReviewForm(FlaskForm):
    """Product review form"""
    rating = SelectField('Rating', 
                        choices=[(1, '1 - Poor'),
                                (2, '2 - Fair'),
                                (3, '3 - Good'),
                                (4, '4 - Very Good'),
                                (5, '5 - Excellent')],
                        coerce=int,
                        validators=[DataRequired()])
    comment = TextAreaField('Your Review', 
                           validators=[Optional(), Length(max=500)])

# Add to Cart Form
class AddToCartForm(FlaskForm):
    """Add product to shopping cart form"""
    size = SelectField('Size', 
                      validators=[DataRequired()])
    color = SelectField('Color', 
                       validators=[DataRequired()])
    quantity = IntegerField('Quantity', 
                           validators=[DataRequired(), NumberRange(min=1)])
