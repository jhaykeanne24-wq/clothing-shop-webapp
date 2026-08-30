from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.models import db, Product
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Home page - Public landing page introducing the store"""
    page = request.args.get('page', 1, type=int)
    featured_products = Product.query.filter_by(is_active=True).limit(6).all()
    
    return render_template('index.html', featured_products=featured_products)

@main_bp.route('/dashboard')
def dashboard():
    """User dashboard - Order history and activity"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    from app.models import Order
    page = request.args.get('page', 1, type=int)
    orders = Order.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=10)
    
    return render_template('dashboard.html', orders=orders)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # Validate input
        if not all([name, email, message]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Send email
        from app.routes.auth_routes import mail
        try:
            msg = Message(
                subject=f'New Contact from {name}',
                recipients=['support@clothingshop.com'],
                body=f'Email: {email}\n\nMessage:\n{message}'
            )
            mail.send(msg)
            return jsonify({'success': 'Message sent successfully'}), 200
        except Exception as e:
            return jsonify({'error': 'Failed to send message'}), 500
    
    return render_template('contact.html')
