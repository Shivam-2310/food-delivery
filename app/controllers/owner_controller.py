"""
RESTAURANT OWNER CONTROLLER FOR RESTAURANT MANAGEMENT
"""

import os
import logging
import uuid
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Restaurant, MenuItem, Order, OrderItem, Feedback
from app.forms.owner_forms import RestaurantForm, MenuItemForm, OrderUpdateForm, FeedbackResponseForm
from app.utils.decorators import owner_required
from sqlalchemy import func, desc
from app.utils.constants import CUISINE_OPTIONS

bp = Blueprint('owner', __name__, url_prefix='/owner')
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """
    CHECK IF FILE HAS ALLOWED EXTENSION
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def save_image(file):
    """
    SAVE UPLOADED IMAGE AND RETURN FILENAME
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # ADD UNIQUE IDENTIFIER TO FILENAME
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
        return unique_filename
    return None

@bp.route('/dashboard')
@login_required
@owner_required
def dashboard():
    """
    RESTAURANT OWNER DASHBOARD ROUTE
    """
    # GET OWNER'S RESTAURANTS
    restaurants = Restaurant.query.filter_by(owner_id=current_user.owner_profile.id).all()
    
    # GET RECENT ORDERS ACROSS ALL RESTAURANTS
    recent_orders = Order.query.join(Restaurant).filter(
        Restaurant.owner_id == current_user.owner_profile.id
    ).order_by(Order.created_at.desc()).limit(10).all()
    
    # GET PENDING FEEDBACK
    pending_feedback = Feedback.query\
        .join(Order, Feedback.order_id == Order.id)\
        .filter(Order.restaurant_id.in_([r.id for r in Restaurant.query.filter_by(owner_id=current_user.owner_profile.id)]),
                Feedback.is_resolved == False)\
        .all()
    
    return render_template('owner/dashboard.html',
                           restaurants=restaurants,
                           recent_orders=recent_orders,
                           pending_feedback=pending_feedback)

@bp.route('/restaurants')
@login_required
@owner_required
def restaurants():
    """
    RESTAURANT MANAGEMENT ROUTE
    """
    restaurants = Restaurant.query.filter_by(owner_id=current_user.owner_profile.id).all()
    return render_template('owner/restaurants.html', restaurants=restaurants)

@bp.route('/restaurant/new', methods=['GET', 'POST'])
@login_required
@owner_required
def new_restaurant():
    """
    CREATE NEW RESTAURANT ROUTE
    """
    form = RestaurantForm()
    # Populate cuisines choices from existing cuisines in DB
    form.cuisines.choices = [(c, c) for c in CUISINE_OPTIONS]
    
    if form.validate_on_submit():
        # HANDLE IMAGE UPLOAD
        image_filename = None
        if form.image.data:
            image_filename = save_image(form.image.data)
        
        # CREATE RESTAURANT
        restaurant = Restaurant(
            owner_id=current_user.owner_profile.id,
            name=form.name.data,
            description=form.description.data,
            location=form.location.data,
            image_path=image_filename
        )
        # Save cuisines list (also sets cuisine_type for compatibility)
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
    """
    RESTAURANT DETAIL ROUTE
    """
    restaurant = Restaurant.query.get_or_404(id)
    
    # ENSURE RESTAURANT BELONGS TO CURRENT USER
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    # GET MENU ITEMS GROUPED BY CATEGORY
    menu_by_category = restaurant.get_menu_by_category()
    
    # GET ORDER FEEDBACK FOR THIS RESTAURANT (primary source for ratings/comments)
    from app.models.feedback import Feedback
    feedback_list = Feedback.query.filter_by(restaurant_id=restaurant.id).order_by(Feedback.created_at.desc()).all()
    
    return render_template('owner/restaurant_detail.html',
                           restaurant=restaurant,
                           menu_by_category=menu_by_category,
                           feedback_list=feedback_list)

@bp.route('/restaurant/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_restaurant(id):
    """
    EDIT RESTAURANT ROUTE
    """
    restaurant = Restaurant.query.get_or_404(id)
    
    # ENSURE RESTAURANT BELONGS TO CURRENT USER
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    form = RestaurantForm()
    # Populate cuisines choices
    form.cuisines.choices = [(c, c) for c in CUISINE_OPTIONS]
    
    if form.validate_on_submit():
        # HANDLE IMAGE UPLOAD
        if form.image.data:
            image_filename = save_image(form.image.data)
            # DELETE OLD IMAGE IF EXISTS
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
    """
    DELETE RESTAURANT ROUTE
    """
    restaurant = Restaurant.query.get_or_404(id)
    
    # ENSURE RESTAURANT BELONGS TO CURRENT USER
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    restaurant_name = restaurant.name
    
    # DELETE RESTAURANT IMAGE IF EXISTS
    if restaurant.image_path:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], restaurant.image_path))
        except OSError:
            pass
    
    # DELETE MENU ITEM IMAGES
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
    """
    RESTAURANT MENU MANAGEMENT ROUTE
    """
    restaurant = Restaurant.query.get_or_404(id)
    
    # ENSURE RESTAURANT BELONGS TO CURRENT USER
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    # GROUP MENU ITEMS BY CATEGORY
    menu_by_category = restaurant.get_menu_by_category()
    
    return render_template('owner/menu.html', 
                           restaurant=restaurant,
                           menu_by_category=menu_by_category)

@bp.route('/restaurant/<int:id>/menu/new', methods=['GET', 'POST'])
@login_required
@owner_required
def new_menu_item(id):
    """
    ADD NEW MENU ITEM ROUTE
    """
    restaurant = Restaurant.query.get_or_404(id)
    
    # ENSURE RESTAURANT BELONGS TO CURRENT USER
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    form = MenuItemForm()
    
    if form.validate_on_submit():
        # HANDLE IMAGE UPLOAD
        image_filename = None
        if form.image.data:
            image_filename = save_image(form.image.data)
        
        # CREATE MENU ITEM
        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            is_vegetarian=form.is_vegetarian.data,
            is_special=form.is_special.data,
            is_deal_of_day=form.is_deal_of_day.data,
            image_path=image_filename
        )
        
        # ENSURE ONLY ONE DEAL OF THE DAY
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
    """
    EDIT MENU ITEM ROUTE
    """
    menu_item = MenuItem.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # ENSURE RESTAURANT BELONGS TO CURRENT USER
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    form = MenuItemForm()
    
    if form.validate_on_submit():
        # HANDLE IMAGE UPLOAD
        if form.image.data:
            image_filename = save_image(form.image.data)
            # DELETE OLD IMAGE IF EXISTS
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
        menu_item.is_vegetarian = form.is_vegetarian.data
        menu_item.is_special = form.is_special.data
        
        # HANDLE DEAL OF THE DAY STATUS
        if form.is_deal_of_day.data and not menu_item.is_deal_of_day:
            # CLEAR OTHER DEAL OF THE DAY ITEMS
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
        form.is_vegetarian.data = menu_item.is_vegetarian
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
    """
    DELETE MENU ITEM ROUTE
    """
    menu_item = MenuItem.query.get_or_404(id)
    restaurant = Restaurant.query.get_or_404(menu_item.restaurant_id)
    
    # ENSURE RESTAURANT BELONGS TO CURRENT USER
    if restaurant.owner_id != current_user.owner_profile.id:
        abort(403)
    
    menu_item_name = menu_item.name
    
    # DELETE MENU ITEM IMAGE IF EXISTS
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
    """
    ORDERS MANAGEMENT ROUTE
    """
    # GET FILTER PARAMETERS
    status_filter = request.args.get('status', '')
    restaurant_id = request.args.get('restaurant_id', '')
    
    # BUILD QUERY TO GET ORDERS FOR OWNER'S RESTAURANTS
    query = Order.query.join(Restaurant).filter(
        Restaurant.owner_id == current_user.owner_profile.id
    )
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    if restaurant_id:
        query = query.filter(Order.restaurant_id == restaurant_id)
    
    # GET ORDERS SORTED BY DATE (NEWEST FIRST)
    orders = query.order_by(Order.created_at.desc()).all()
    
    # GET OWNER'S RESTAURANTS FOR FILTER
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
    """
    ORDER DETAIL AND STATUS UPDATE ROUTE
    """
    order = Order.query.get_or_404(id)
    
    # ENSURE ORDER IS FROM OWNER'S RESTAURANT
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
    
    # EXPLICITLY LOAD FEEDBACK FOR THIS ORDER
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
    """
    REPORTS DASHBOARD ROUTE
    """
    # GET FILTER PARAMETERS
    restaurant_id = request.args.get('restaurant_id', '')
    
    # GET OWNER'S RESTAURANTS
    restaurants = Restaurant.query.filter_by(owner_id=current_user.owner_profile.id).all()
    
    if restaurant_id:
        # ENSURE RESTAURANT BELONGS TO CURRENT USER
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant or restaurant.owner_id != current_user.owner_profile.id:
            abort(403)
        
        # TOP 5 MOST ORDERED MENU ITEMS
        top_items = db.session.query(
            MenuItem.id, MenuItem.name, func.sum(OrderItem.quantity).label('total')
        ).join(OrderItem).join(Order)\
        .filter(MenuItem.restaurant_id == restaurant_id)\
        .group_by(MenuItem.id, MenuItem.name)\
        .order_by(desc('total'))\
        .limit(5).all()
        
        # TOTAL ORDERS AND REVENUE FOR RESTAURANT
        orders_count = Order.query.filter_by(restaurant_id=restaurant_id).count()
        total_revenue = db.session.query(func.sum(Order.total_amount))\
            .filter(Order.restaurant_id == restaurant_id)\
            .scalar() or 0
        
        # AVERAGE RATING - Use the restaurant's average_rating property
        restaurant = Restaurant.query.get(restaurant_id)
        avg_rating = restaurant.average_rating
        
        # ORDERS BY DAY (LAST 30 DAYS)
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
        
        # REVENUE TREND (LAST 30 DAYS)
        daily_revenue = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.restaurant_id == restaurant_id,
            Order.created_at >= start_date
        ).group_by(func.date(Order.created_at))\
        .order_by(func.date(Order.created_at)).all()
    else:
        # INITIALIZE VARIABLES
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
    """
    FEEDBACK MANAGEMENT ROUTE
    """
    # GET FEEDBACK FOR OWNER'S RESTAURANTS
    feedback_list = Feedback.query\
        .join(Order, Feedback.order_id == Order.id)\
        .filter(Order.restaurant_id.in_([r.id for r in Restaurant.query.filter_by(owner_id=current_user.owner_profile.id)]))\
        .order_by(Feedback.created_at.desc()).all()
    
    return render_template('owner/feedback.html', feedback_list=feedback_list)

@bp.route('/feedback/<int:id>/respond', methods=['GET', 'POST'])
@login_required
@owner_required
def respond_to_feedback(id):
    """
    RESPOND TO FEEDBACK ROUTE
    """
    feedback_item = Feedback.query.get_or_404(id)
    
    # VERIFY FEEDBACK IS FOR OWNER'S RESTAURANT
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
        
        # Redirect back to order detail if coming from there
        if request.args.get('from_order'):
            return redirect(url_for('owner.order_detail', id=feedback_item.order_id))
        
        # Otherwise go to feedback list
        return redirect(url_for('owner.feedback'))
    
    return render_template('owner/respond_to_feedback.html',
                           feedback=feedback_item,
                           form=form)
