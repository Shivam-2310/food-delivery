"""Restaurant owner controller for restaurant management."""

import logging
import os
import uuid

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    current_app,
    abort,
)
from flask_login import current_user, login_required
from sqlalchemy import desc, func
from werkzeug.utils import secure_filename

from app import db
from app.forms.owner_forms import (
    FeedbackResponseForm,
    MenuItemForm,
    OrderUpdateForm,
    RestaurantForm,
)
from app.models import Feedback, MenuItem, Order, OrderItem, Restaurant
from app.models.dish_rating import DishRating
from app.utils.constants import CUISINE_OPTIONS
from app.utils.decorators import owner_required

bp = Blueprint('owner', __name__, url_prefix='/owner')
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def save_image(file):
    """Save uploaded image and return filename."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add unique identifier to filename.
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
        return unique_filename
    return None

@bp.route('/dashboard')
@login_required
@owner_required
def dashboard():
    """Restaurant owner dashboard route."""
    # Get owner's restaurants.
    restaurants = Restaurant.query.filter_by(owner_id=current_user.owner_profile.id).all()
    
    # Get recent orders across all restaurants.
    recent_orders = Order.query.join(Restaurant).filter(
        Restaurant.owner_id == current_user.owner_profile.id
    ).order_by(Order.created_at.desc()).limit(10).all()
    
    # Get pending feedback.
    pending_feedback = Feedback.query\
        .join(Order, Feedback.order_id == Order.id)\
        .filter(Order.restaurant_id.in_([r.id for r in Restaurant.query.filter_by(owner_id=current_user.owner_profile.id)]),
                Feedback.is_resolved == False)\
        .all()
    
    # Get recent dish ratings.
    recent_dish_ratings = DishRating.query\
        .join(MenuItem, DishRating.menu_item_id == MenuItem.id)\
        .filter(MenuItem.restaurant_id.in_([r.id for r in restaurants]))\
        .order_by(DishRating.created_at.desc()).limit(10).all()
    
    # Get dish rating statistics.
    dish_rating_stats = {}
    for restaurant in restaurants:
        total_dish_ratings = DishRating.query.join(MenuItem).filter(
            MenuItem.restaurant_id == restaurant.id
        ).count()
        
        avg_dish_rating = db.session.query(func.avg(DishRating.rating)).join(MenuItem).filter(
            MenuItem.restaurant_id == restaurant.id
        ).scalar() or 0
        
        dish_rating_stats[restaurant.id] = {
            'total_ratings': total_dish_ratings,
            'average_rating': round(avg_dish_rating, 1) if avg_dish_rating else 0
        }
    
    return render_template('owner/dashboard.html',
                           restaurants=restaurants,
                           recent_orders=recent_orders,
                           pending_feedback=pending_feedback,
                           recent_dish_ratings=recent_dish_ratings,
                           dish_rating_stats=dish_rating_stats)

@bp.route('/restaurants')
@login_required
@owner_required
def restaurants():
    """Restaurant management route."""
    # Get search parameters.
    search_query = request.args.get('search', '').strip()
    
    # Build query to get restaurants for owner.
    query = Restaurant.query.filter_by(owner_id=current_user.owner_profile.id)
    
    # Apply search filter.
    if search_query:
        query = query.filter(
            db.or_(
                Restaurant.name.ilike(f'%{search_query}%'),
                Restaurant.location.ilike(f'%{search_query}%'),
                Restaurant.description.ilike(f'%{search_query}%')
            )
        )
    
    # Get restaurants sorted by name.
    restaurants = query.order_by(Restaurant.name.asc()).all()
    
    return render_template('owner/restaurants.html', 
                           restaurants=restaurants,
                           search_query=search_query)

@bp.route('/restaurant/new', methods=['GET', 'POST'])
@login_required
@owner_required
def new_restaurant():
    """Create new restaurant route."""
    form = RestaurantForm()
    # Populate cuisines choices from existing cuisines in DB.
    form.cuisines.choices = [(c, c) for c in CUISINE_OPTIONS]
    
    if form.validate_on_submit():
        # Handle image upload.
        image_filename = None
        if form.image.data:
            image_filename = save_image(form.image.data)
        
        # Create restaurant.
        restaurant = Restaurant(
            owner_id=current_user.owner_profile.id,
            name=form.name.data,
            description=form.description.data,
            location=form.location.data,
            image_path=image_filename
        )
        # Save cuisines list (also sets cuisine_type for compatibility).
        restaurant.set_cuisines(form.cuisines.data)
        
        db.session.add(restaurant)
        db.session.commit()
        
        logger.info(f"Restaurant '{restaurant.name}' created by {current_user.username}")
        flash(f"RESTAURANT '{restaurant.name}' CREATED SUCCESSFULLY.", "success")
        return redirect(url_for('owner.restaurant_detail', id=restaurant.id))
    
    return render_template('owner/restaurant_form.html', form=form, title="ADD NEW RESTAURANT", CUISINE_OPTIONS=CUISINE_OPTIONS)

@bp.route('/restaurant/<int:id>')
@login_required
@owner_required
def restaurant_detail(id):
    """Restaurant detail route."""
    restaurant = Restaurant.query.get_or_404(id)
    
    # Ensure restaurant belongs to current user.
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    # Get menu items grouped by category.
    menu_by_category = restaurant.get_menu_by_category()
    
    # Get order feedback for this restaurant (primary source for ratings/comments).
    from app.models.feedback import Feedback
    feedback_list = Feedback.query.filter_by(restaurant_id=restaurant.id).order_by(Feedback.created_at.desc()).all()
    
    # Get dish ratings for this restaurant.
    dish_ratings_list = DishRating.query.join(MenuItem).filter(
        MenuItem.restaurant_id == restaurant.id
    ).order_by(DishRating.created_at.desc()).all()
    
    return render_template('owner/restaurant_detail.html',
                           restaurant=restaurant,
                           menu_by_category=menu_by_category,
                           feedback_list=feedback_list,
                           dish_ratings_list=dish_ratings_list)

@bp.route('/restaurant/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_restaurant(id):
    """Edit restaurant route."""
    restaurant = Restaurant.query.get_or_404(id)
    
    # Ensure restaurant belongs to current user.
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    form = RestaurantForm()
    # Populate cuisines choices.
    form.cuisines.choices = [(c, c) for c in CUISINE_OPTIONS]
    
    if form.validate_on_submit():
        # Handle image upload.
        if form.image.data:
            image_filename = save_image(form.image.data)
            # Delete old image if exists.
            if restaurant.image_path:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], restaurant.image_path))
                except OSError:
                    pass
            restaurant.image_path = image_filename
        
        restaurant.name = form.name.data
        restaurant.description = form.description.data
        restaurant.location = form.location.data
        restaurant.set_cuisines(form.cuisines.data)
        
        db.session.commit()
        
        logger.info(f"Restaurant '{restaurant.name}' updated by {current_user.username}")
        flash(f"RESTAURANT '{restaurant.name}' UPDATED SUCCESSFULLY.", "success")
        return redirect(url_for('owner.restaurant_detail', id=restaurant.id))
    
    elif request.method == 'GET':
        form.name.data = restaurant.name
        form.description.data = restaurant.description
        form.location.data = restaurant.location
        form.cuisines.data = restaurant.get_cuisines()
    
    return render_template('owner/restaurant_form.html', 
                           form=form, 
                           restaurant=restaurant,
                           title="EDIT RESTAURANT",
                           CUISINE_OPTIONS=CUISINE_OPTIONS)

@bp.route('/restaurant/<int:id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_restaurant(id):
    """Delete restaurant route."""
    restaurant = Restaurant.query.get_or_404(id)
    
    # Ensure restaurant belongs to current user.
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    restaurant_name = restaurant.name
    
    # Delete restaurant image if exists.
    if restaurant.image_path:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], restaurant.image_path))
        except OSError:
            pass
    
    # Delete menu item images.
    for item in restaurant.menu_items:
        if item.image_path:
            try:
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], item.image_path))
            except OSError:
                pass
    
    db.session.delete(restaurant)
    db.session.commit()
    
    logger.info(f"Restaurant '{restaurant_name}' deleted by {current_user.username}")
    flash(f"RESTAURANT '{restaurant_name}' DELETED SUCCESSFULLY.", "success")
    return redirect(url_for('owner.restaurants'))

@bp.route('/restaurant/<int:id>/menu')
@login_required
@owner_required
def restaurant_menu(id):
    """Restaurant menu management route."""
    restaurant = Restaurant.query.get_or_404(id)
    
    # Ensure restaurant belongs to current user.
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    # Group menu items by category.
    menu_by_category = restaurant.get_menu_by_category()
    
    return render_template('owner/menu.html', 
                           restaurant=restaurant,
                           menu_by_category=menu_by_category)

@bp.route('/restaurant/<int:id>/menu/new', methods=['GET', 'POST'])
@login_required
@owner_required
def new_menu_item(id):
    """Add new menu item route."""
    restaurant = Restaurant.query.get_or_404(id)
    
    # Ensure restaurant belongs to current user.
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    form = MenuItemForm()
    
    if form.validate_on_submit():
        # Validate dietary preferences: cannot be vegan and non-vegetarian.
        is_non_vegetarian = form.is_vegetarian.data  # True when "Non-Vegetarian" is checked.
        is_vegan = form.is_vegan.data
        
        if is_vegan and is_non_vegetarian:
            flash("ERROR: A dish cannot be both Vegan and Non-Vegetarian at the same time!", "error")
            return render_template('owner/menu_item_form.html', form=form, restaurant=restaurant)
        
        # Handle image upload.
        image_filename = None
        if form.image.data:
            image_filename = save_image(form.image.data)
        
        # Create menu item.
        # Note: form.is_vegetarian.data is True when "Non-Vegetarian" is checked.
        # So we need to invert it for the database field.
        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            is_vegetarian=not form.is_vegetarian.data,  # Invert: unchecked = vegetarian, checked = non-vegetarian.
            is_vegan=form.is_vegan.data,
            is_guilt_free=form.is_guilt_free.data,
            is_special=form.is_special.data,
            is_deal_of_day=form.is_deal_of_day.data,
            image_path=image_filename
        )
        
        # Ensure only one deal of the day.
        if form.is_deal_of_day.data:
            existing_deals = MenuItem.query.filter_by(
                restaurant_id=restaurant.id,
                is_deal_of_day=True
            ).all()
            for item in existing_deals:
                item.is_deal_of_day = False
        
        db.session.add(menu_item)
        db.session.commit()
        
        logger.info(f"Menu item '{menu_item.name}' created by {current_user.username}")
        flash(f"MENU ITEM '{menu_item.name}' ADDED SUCCESSFULLY.", "success")
        return redirect(url_for('owner.restaurant_menu', id=restaurant.id))
    
    return render_template('owner/menu_item_form.html', 
                           form=form, 
                           restaurant=restaurant,
                           title="ADD NEW MENU ITEM")

@bp.route('/menu-item/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_menu_item(id):
    """Edit menu item route."""
    menu_item = MenuItem.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # Ensure restaurant belongs to current user.
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    form = MenuItemForm()
    
    if form.validate_on_submit():
        # Validate dietary preferences: cannot be vegan and non-vegetarian.
        is_non_vegetarian = form.is_vegetarian.data  # True when "Non-Vegetarian" is checked.
        is_vegan = form.is_vegan.data
        
        if is_vegan and is_non_vegetarian:
            flash("ERROR: A dish cannot be both Vegan and Non-Vegetarian at the same time!", "error")
            return render_template('owner/menu_item_form.html', form=form, restaurant=restaurant, menu_item=menu_item)
        
        # Handle image upload.
        if form.image.data:
            image_filename = save_image(form.image.data)
            # Delete old image if exists.
            if menu_item.image_path:
                try:
                    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], menu_item.image_path))
                except OSError:
                    pass
            menu_item.image_path = image_filename
        
        menu_item.name = form.name.data
        menu_item.description = form.description.data
        menu_item.price = form.price.data
        menu_item.category = form.category.data
        menu_item.is_vegetarian = not form.is_vegetarian.data  # Invert: unchecked = vegetarian, checked = non-vegetarian.
        menu_item.is_vegan = form.is_vegan.data
        menu_item.is_guilt_free = form.is_guilt_free.data
        menu_item.is_special = form.is_special.data
        
        # Handle deal of the day status.
        if form.is_deal_of_day.data and not menu_item.is_deal_of_day:
            # Clear other deal of the day items.
            existing_deals = MenuItem.query.filter_by(
                restaurant_id=restaurant.id,
                is_deal_of_day=True
            ).all()
            for item in existing_deals:
                item.is_deal_of_day = False
        
        menu_item.is_deal_of_day = form.is_deal_of_day.data
        
        db.session.commit()
        
        logger.info(f"Menu item '{menu_item.name}' updated by {current_user.username}")
        flash(f"MENU ITEM '{menu_item.name}' UPDATED SUCCESSFULLY.", "success")
        return redirect(url_for('owner.restaurant_menu', id=restaurant.id))
    
    elif request.method == 'GET':
        form.name.data = menu_item.name
        form.description.data = menu_item.description
        form.price.data = menu_item.price
        form.category.data = menu_item.category
        # Invert the vegetarian status for the form since "Non-Vegetarian" is checked when item is non-veg.
        form.is_vegetarian.data = not menu_item.is_vegetarian
        form.is_vegan.data = menu_item.is_vegan
        form.is_guilt_free.data = menu_item.is_guilt_free
        form.is_special.data = menu_item.is_special
        form.is_deal_of_day.data = menu_item.is_deal_of_day
    
    return render_template('owner/menu_item_form.html', 
                           form=form, 
                           restaurant=restaurant,
                           menu_item=menu_item,
                           title="EDIT MENU ITEM")

@bp.route('/menu-item/<int:id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_menu_item(id):
    """Delete menu item route."""
    menu_item = MenuItem.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # Ensure restaurant belongs to current user.
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    menu_item_name = menu_item.name
    
    # Delete menu item image if exists.
    if menu_item.image_path:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], menu_item.image_path))
        except OSError:
            pass
    
    db.session.delete(menu_item)
    db.session.commit()
    
    logger.info(f"Menu item '{menu_item_name}' deleted by {current_user.username}")
    flash(f"MENU ITEM '{menu_item_name}' DELETED SUCCESSFULLY.", "success")
    return redirect(url_for('owner.restaurant_menu', id=restaurant.id))

@bp.route('/orders')
@login_required
@owner_required
def orders():
    """Orders management route."""
    # Get filter parameters.
    status_filter = request.args.get('status', '')
    restaurant_id = request.args.get('restaurant_id', '')
    
    # Build query to get orders for owner's restaurants.
    query = Order.query.join(Restaurant).filter(
        Restaurant.owner_id == current_user.owner_profile.id
    )
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    if restaurant_id:
        query = query.filter(Order.restaurant_id == restaurant_id)
    
    # Get orders sorted by date (newest first).
    orders = query.order_by(Order.created_at.desc()).all()
    
    # Get owner's restaurants for filter.
    restaurants = Restaurant.query.filter_by(owner_id=current_user.owner_profile.id).all()
    
    return render_template('owner/orders.html', 
                           orders=orders,
                           status_filter=status_filter,
                           restaurant_id=restaurant_id,
                           restaurants=restaurants)

@bp.route('/order/<int:id>', methods=['GET', 'POST'])
@login_required
@owner_required
def order_detail(id):
    """Order detail and status update route."""
    order = Order.query.get_or_404(id)
    
    # Ensure order is from owner's restaurant.
    restaurant = Restaurant.query.get(order.restaurant_id)
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    form = OrderUpdateForm()
    
    if form.validate_on_submit():
        order.update_status(form.status.data)
        db.session.commit()
        
        logger.info(f"Order #{order.id} status updated to {form.status.data} by {current_user.username}")
        flash(f"ORDER STATUS UPDATED SUCCESSFULLY.", "success")
        return redirect(url_for('owner.order_detail', id=order.id))
    
    elif request.method == 'GET':
        form.status.data = order.status
    
    # Explicitly load feedback for this order.
    from app.models.feedback import Feedback
    feedback = Feedback.query.filter_by(order_id=order.id).first()
    
    return render_template('owner/order_detail.html', 
                           order=order,
                           form=form,
                           existing_feedback=feedback)

@bp.route('/reports')
@login_required
@owner_required
def reports():
    """Reports dashboard route."""
    # Get filter parameters.
    restaurant_id = request.args.get('restaurant_id', '')
    
    # Get owner's restaurants.
    restaurants = Restaurant.query.filter_by(owner_id=current_user.owner_profile.id).all()
    
    if restaurant_id:
        # Ensure restaurant belongs to current user.
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant or restaurant.owner_id != current_user.owner_profile.id:
            abort(403)
        
        # Top 5 most ordered menu items.
        top_items = db.session.query(
            MenuItem.id, MenuItem.name, func.sum(OrderItem.quantity).label('total')
        ).join(OrderItem).join(Order)\
        .filter(MenuItem.restaurant_id == restaurant_id)\
        .group_by(MenuItem.id, MenuItem.name)\
        .order_by(desc('total'))\
        .limit(5).all()
        
        # Total orders and revenue for restaurant.
        orders_count = Order.query.filter_by(restaurant_id=restaurant_id).count()
        total_revenue = db.session.query(func.sum(Order.total_amount))\
            .filter(Order.restaurant_id == restaurant_id)\
            .scalar() or 0
        
        # Average rating: use the restaurant's average_rating property.
        restaurant = Restaurant.query.get(restaurant_id)
        avg_rating = restaurant.average_rating
        
        # Orders by day (last 30 days).
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        daily_orders = db.session.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('count')
        ).filter(
            Order.restaurant_id == restaurant_id,
            Order.created_at >= start_date
        ).group_by(func.date(Order.created_at))\
        .order_by(func.date(Order.created_at)).all()
        
        # Revenue trend (last 30 days).
        daily_revenue = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.restaurant_id == restaurant_id,
            Order.created_at >= start_date
        ).group_by(func.date(Order.created_at))\
        .order_by(func.date(Order.created_at)).all()
    else:
        # Initialize variables.
        top_items = []
        orders_count = 0
        total_revenue = 0
        avg_rating = 0
        daily_orders = []
        daily_revenue = []
    
    return render_template('owner/reports.html',
                           restaurants=restaurants,
                           restaurant_id=restaurant_id,
                           top_items=top_items,
                           orders_count=orders_count,
                           total_revenue=total_revenue,
                           avg_rating=avg_rating,
                           daily_orders=daily_orders,
                           daily_revenue=daily_revenue)

@bp.route('/feedback')
@login_required
@owner_required
def feedback():
    """Feedback management route."""
    # Get feedback for owner's restaurants.
    feedback_list = Feedback.query\
        .join(Order, Feedback.order_id == Order.id)\
        .filter(Order.restaurant_id.in_([r.id for r in Restaurant.query.filter_by(owner_id=current_user.owner_profile.id)]))\
        .order_by(Feedback.created_at.desc()).all()
    
    return render_template('owner/feedback.html', feedback_list=feedback_list)

@bp.route('/feedback/<int:id>/respond', methods=['GET', 'POST'])
@login_required
@owner_required
def respond_to_feedback(id):
    """Respond to feedback route."""
    feedback_item = Feedback.query.get_or_404(id)
    
    # Verify feedback is for owner's restaurant.
    is_for_owner = Restaurant.query.filter_by(
        id=feedback_item.restaurant_id, 
        owner_id=current_user.owner_profile.id
    ).first() is not None
    
    if not is_for_owner:
        abort(403)
    
    form = FeedbackResponseForm()
    
    if form.validate_on_submit():
        feedback_item.response = form.response.data
        feedback_item.is_resolved = True
        db.session.commit()
        
        logger.info(f"Feedback #{feedback_item.id} responded to by {current_user.username}")
        flash("YOUR RESPONSE HAS BEEN SUBMITTED.", "success")
        
        # Redirect back to order detail if coming from there.
        if request.args.get('from_order'):
            return redirect(url_for('owner.order_detail', id=feedback_item.order_id))
        
        # Otherwise go to feedback list.
        return redirect(url_for('owner.feedback'))
    
    return render_template('owner/respond_to_feedback.html',
                           feedback=feedback_item,
                           form=form)
