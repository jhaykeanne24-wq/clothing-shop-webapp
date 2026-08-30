from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, CartItem, Product, Order, OrderItem
from app.forms import AddToCartForm
from app.routes.auth_routes import send_order_confirmation_email
import secrets
from datetime import datetime

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    """Display shopping cart"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    return render_template('cart/view_cart.html', cart_items=cart_items, total_price=total_price)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to shopping cart"""
    product = Product.query.get_or_404(product_id)
    
    # Get form data
    size = request.form.get('size')
    color = request.form.get('color')
    quantity = request.form.get('quantity', 1, type=int)
    
    # Validate quantity
    if quantity < 1 or quantity > product.stock_quantity:
        flash('Invalid quantity. Please check stock availability.', 'danger')
        return redirect(url_for('product.product_detail', product_id=product_id))
    
    # Check if item already in cart
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
        size=size,
        color=color
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity,
            size=size,
            color=color
        )
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update/<int:cart_item_id>', methods=['POST'])
@login_required
def update_cart_item(cart_item_id):
    """Update cart item quantity"""
    cart_item = CartItem.query.get_or_404(cart_item_id)
    
    # Ensure user owns this cart item
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity < 1:
        db.session.delete(cart_item)
    else:
        if quantity > cart_item.product.stock_quantity:
            flash('Insufficient stock.', 'danger')
            return redirect(url_for('cart.view_cart'))
        cart_item.quantity = quantity
    
    db.session.commit()
    flash('Cart updated!', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    cart_item = CartItem.query.get_or_404(cart_item_id)
    
    # Ensure user owns this cart item
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout and place order"""
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    if request.method == 'POST':
        # Get shipping information
        shipping_address = request.form.get('shipping_address')
        shipping_city = request.form.get('shipping_city')
        shipping_postal = request.form.get('shipping_postal')
        shipping_country = request.form.get('shipping_country')
        
        # Validate shipping information
        if not all([shipping_address, shipping_city, shipping_postal, shipping_country]):
            flash('Please fill in all shipping information.', 'danger')
            return render_template('cart/checkout.html', cart_items=cart_items, user=current_user)
        
        # Calculate total
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        # Create order
        order = Order(
            user_id=current_user.id,
            order_number=f'ORD-{secrets.token_hex(8).upper()}',
            total_amount=total_amount,
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_postal=shipping_postal,
            shipping_country=shipping_country,
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Add order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                size=cart_item.size,
                color=cart_item.color,
                price_at_purchase=cart_item.product.price
            )
            
            # Update product stock
            cart_item.product.stock_quantity -= cart_item.quantity
            db.session.add(order_item)
        
        # Clear cart
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        
        # Send order confirmation email
        send_order_confirmation_email(current_user, order)
        
        flash('Order placed successfully! You will receive a confirmation email shortly.', 'success')
        return redirect(url_for('user.order_detail', order_id=order.id))
    
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart/checkout.html', cart_items=cart_items, total_price=total_price, user=current_user)

@cart_bp.route('/count')
@login_required
def cart_count():
    """Get cart item count (for AJAX)"""
    count = CartItem.query.filter_by(user_id=current_user.id).count()
    return jsonify({'count': count})
