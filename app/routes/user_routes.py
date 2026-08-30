from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, Order, OrderItem
from app.forms import ProfileUpdateForm

user_bp = Blueprint('user', __name__, url_prefix='/profile')

@user_bp.route('/')
@login_required
def profile():
    """Display user profile - Profile Management"""
    form = ProfileUpdateForm()
    return render_template('user/profile.html', user=current_user, form=form)

@user_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        # Check if username or email already exists (excluding current user)
        existing_user = User.query.filter(
            (User.username == form.username.data) & (User.id != current_user.id)
        ).first()
        
        if existing_user:
            flash('Username already taken.', 'danger')
            return redirect(url_for('user.edit_profile'))
        
        existing_email = User.query.filter(
            (User.email == form.email.data) & (User.id != current_user.id)
        ).first()
        
        if existing_email:
            flash('Email already registered.', 'danger')
            return redirect(url_for('user.edit_profile'))
        
        # Update user profile
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.postal_code = form.postal_code.data
        current_user.country = form.country.data
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
        form.address.data = current_user.address
        form.city.data = current_user.city
        form.postal_code.data = current_user.postal_code
        form.country.data = current_user.country
    
    return render_template('user/edit_profile.html', form=form)

@user_bp.route('/orders')
@login_required
def orders():
    """View order history"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template('user/orders.html', orders=orders)

@user_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    
    # Ensure user can only view their own orders
    if order.user_id != current_user.id:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('user.orders'))
    
    return render_template('user/order_detail.html', order=order)
