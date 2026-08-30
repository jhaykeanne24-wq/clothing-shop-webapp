from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app.forms import RegistrationForm, LoginForm
from app import mail
from flask_mail import Message
import secrets
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email confirmation"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Send confirmation email
            send_welcome_email(user)
            
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login with session management"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            session.permanent = True
            
            next_page = request.args.get('next')
            if not next_page or url_has_allowed_host_and_scheme(next_page):
                next_page = url_for('main.dashboard')
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

def send_welcome_email(user):
    """Send welcome email to new user - SMTP Integration"""
    try:
        subject = 'Welcome to Clothing Shop!'
        sender = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@clothingshop.com')
        recipients = [user.email]
        html_body = f"""
        <html>
            <body>
                <h2>Welcome, {user.username}!</h2>
                <p>Thank you for creating an account at Clothing Shop.</p>
                <p>We're excited to have you as part of our community. Start exploring our collection of premium clothing.</p>
                <p>Happy shopping!</p>
                <p>Best regards,<br>Clothing Shop Team</p>
            </body>
        </html>
        """
        msg = Message(subject=subject, recipients=recipients, html=html_body)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def send_order_confirmation_email(user, order):
    """Send order confirmation email"""
    try:
        subject = f'Order Confirmation - Order #{order.order_number}'
        recipients = [user.email]
        html_body = f"""
        <html>
            <body>
                <h2>Order Confirmation</h2>
                <p>Hi {user.username},</p>
                <p>Thank you for your order!</p>
                <p><strong>Order Number:</strong> {order.order_number}</p>
                <p><strong>Total Amount:</strong> ${order.total_amount:.2f}</p>
                <p>We will notify you when your order is shipped.</p>
                <p>Best regards,<br>Clothing Shop Team</p>
            </body>
        </html>
        """
        msg = Message(subject=subject, recipients=recipients, html=html_body)
        mail.send(msg)
    except Exception as e:
        print(f"Error sending order email: {e}")

def url_has_allowed_host_and_scheme(url, allowed_hosts=None, require_https=False):
    """Check if URL is safe for redirect"""
    if allowed_hosts is None:
        allowed_hosts = ['localhost', '127.0.0.1']
    
    if url.startswith('/'):
        return True
    return False
