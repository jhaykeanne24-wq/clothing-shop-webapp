from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Product, Review
from app.forms import ProductForm, ReviewForm
from sqlalchemy import func

product_bp = Blueprint('product', __name__, url_prefix='/products')

@product_bp.route('/')
def products():
    """Display all products - CRUD Read"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'newest')
    
    query = Product.query.filter_by(is_active=True)
    
    # Filter by category
    if category:
        query = query.filter_by(category=category)
    
    # Search products
    if search:
        query = query.filter(
            Product.name.ilike(f'%{search}%') | 
            Product.description.ilike(f'%{search}%')
        )
    
    # Sort products
    if sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'rating':
        query = query.order_by(Product.rating.desc())
    else:  # newest
        query = query.order_by(Product.created_at.desc())
    
    products = query.paginate(page=page, per_page=12)
    categories = db.session.query(Product.category.distinct()).all()
    
    return render_template('products/products.html', 
                         products=products, 
                         categories=categories,
                         current_category=category,
                         search_query=search,
                         sort_by=sort_by)

@product_bp.route('/<int:product_id>')
def product_detail(product_id):
    """Display product details - CRUD Read"""
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    
    form = ReviewForm() if current_user.is_authenticated else None
    
    return render_template('products/product_detail.html', 
                         product=product, 
                         reviews=reviews,
                         form=form)

@product_bp.route('/<int:product_id>/review', methods=['POST'])
@login_required
def add_review(product_id):
    """Add product review"""
    product = Product.query.get_or_404(product_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(
            product_id=product_id,
            user_id=current_user.id
        ).first()
        
        if existing_review:
            flash('You have already reviewed this product.', 'warning')
            return redirect(url_for('product.product_detail', product_id=product_id))
        
        review = Review(
            product_id=product_id,
            user_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        db.session.add(review)
        
        # Update product rating
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(product_id=product_id).scalar()
        product.rating = float(avg_rating) if avg_rating else 0
        
        db.session.commit()
        flash('Review added successfully!', 'success')
    
    return redirect(url_for('product.product_detail', product_id=product_id))

@product_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_product():
    """Create new product - CRUD Create (Admin only)"""
    # Check if user is admin (you can implement role-based access)
    form = ProductForm()
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            category=form.category.data,
            price=float(form.price.data),
            cost_price=float(form.cost_price.data) if form.cost_price.data else None,
            stock_quantity=form.stock_quantity.data,
            size_options=form.size_options.data,
            color_options=form.color_options.data
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('product.product_detail', product_id=product.id))
    
    return render_template('products/create_product.html', form=form)

@product_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit product - CRUD Update (Admin only)"""
    product = Product.query.get_or_404(product_id)
    form = ProductForm()
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.category = form.category.data
        product.price = float(form.price.data)
        product.cost_price = float(form.cost_price.data) if form.cost_price.data else None
        product.stock_quantity = form.stock_quantity.data
        product.size_options = form.size_options.data
        product.color_options = form.color_options.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product.product_detail', product_id=product.id))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.category.data = product.category
        form.price.data = product.price
        form.cost_price.data = product.cost_price
        form.stock_quantity.data = product.stock_quantity
        form.size_options.data = product.size_options
        form.color_options.data = product.color_options
    
    return render_template('products/edit_product.html', form=form, product=product)

@product_bp.route('/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product - CRUD Delete (Admin only)"""
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product.products'))
