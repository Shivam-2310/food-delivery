"""
CUSTOMER CONTROLLER FOR CUSTOMER FEATURES
"""

import logging
import json
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort, session
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app import db
from app.models import User, Customer, Restaurant, MenuItem, Order, OrderItem, Review, Feedback
from app.models import STATUS_COMPLETED
from app.models import STATUS_PENDING, STATUS_CONFIRMED, STATUS_PREPARING, STATUS_READY, STATUS_COMPLETED
from app.forms.customer_forms import ProfileUpdateForm, PreferencesForm, ReviewForm, OrderFeedbackForm, SearchForm
from app.utils.decorators import customer_required
from app.utils.constants import CUISINE_OPTIONS

bp = Blueprint('customer', __name__, url_prefix='/customer')
logger = logging.getLogger(__name__)

@bp.route('/dashboard')
@login_required
@customer_required
def dashboard():
    """
    CUSTOMER DASHBOARD ROUTE
    """
    # GET RECENT ORDERS
    recent_orders = Order.query.filter_by(customer_id=current_user.customer_profile.id)\
        .order_by(Order.created_at.desc()).limit(5).all()
    
    # GET FAVORITE RESTAURANTS
    favorites = []
    customer_prefs = current_user.customer_profile.get_preferences()
    if customer_prefs and 'favorite_restaurants' in customer_prefs:
        favorites = Restaurant.query.filter(Restaurant.id.in_(customer_prefs['favorite_restaurants'])).all()
    
    # GET RECOMMENDED RESTAURANTS BASED ON PREFERENCES AND HISTORY
    recommended = get_recommendations(current_user.customer_profile)
    
    return render_template('customer/dashboard.html', 
                           recent_orders=recent_orders,
                           favorites=favorites,
                           recommended=recommended)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
@customer_required
def profile():
    """
    CUSTOMER PROFILE ROUTE
    """
    form = ProfileUpdateForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.customer_profile.name = form.name.data
        current_user.customer_profile.phone = form.phone.data
        current_user.customer_profile.address = form.address.data
        
        db.session.commit()
        logger.info(f"Customer profile updated: {current_user.username}")
        flash("YOUR PROFILE HAS BEEN UPDATED SUCCESSFULLY.", "success")
        return redirect(url_for('customer.profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.customer_profile.name
        form.phone.data = current_user.customer_profile.phone
        form.address.data = current_user.customer_profile.address
    
    return render_template('customer/profile.html', form=form)

@bp.route('/preferences', methods=['GET', 'POST'])
@login_required
@customer_required
def preferences():
    """
    CUSTOMER PREFERENCES ROUTE
    """
    # GET ALL CUISINE TYPES FROM DB FOR THE FORM CHOICES (supports multi-cuisine)
    cuisine_choices = [(c, c) for c in CUISINE_OPTIONS]
    
    form = PreferencesForm()
    form.favorite_cuisines.choices = cuisine_choices
    
    if form.validate_on_submit():
        # UPDATE PREFERENCES
        prefs = current_user.customer_profile.get_preferences()
        if not prefs:
            prefs = {}
        
        prefs['favorite_cuisines'] = form.favorite_cuisines.data
        current_user.customer_profile.set_preferences(prefs)
        
        # UPDATE DIETARY RESTRICTIONS
        current_user.customer_profile.set_dietary_restrictions(form.dietary_restrictions.data)
        
        db.session.commit()
        logger.info(f"Customer preferences updated: {current_user.username}")
        flash("YOUR PREFERENCES HAVE BEEN UPDATED SUCCESSFULLY.", "success")
        return redirect(url_for('customer.preferences'))
    
    elif request.method == 'GET':
        # POPULATE FORM WITH EXISTING PREFERENCES
        prefs = current_user.customer_profile.get_preferences()
        if prefs and 'favorite_cuisines' in prefs:
            form.favorite_cuisines.data = prefs['favorite_cuisines']
        
        # POPULATE FORM WITH EXISTING DIETARY RESTRICTIONS
        form.dietary_restrictions.data = current_user.customer_profile.get_dietary_restrictions()
    
    # GET FAVORITE RESTAURANTS FOR DISPLAY
    customer_prefs = current_user.customer_profile.get_preferences()
    favorites = []
    if customer_prefs and 'favorite_restaurants' in customer_prefs:
        favorites = Restaurant.query.filter(Restaurant.id.in_(customer_prefs['favorite_restaurants'])).all()
    
    return render_template('customer/preferences.html', form=form, favorites=favorites)

@bp.route('/restaurants')
@login_required
@customer_required
def restaurants():
    """
    RESTAURANTS LISTING ROUTE
    """
    search_form = SearchForm()
    
    # GET ALL CUISINE TYPES FOR FILTER (multi-select)
    search_form.cuisines.choices = [(c, c) for c in CUISINE_OPTIONS]
    
    # GET QUERY PARAMETERS
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    cuisines_selected = request.args.getlist('cuisines')
    # Pre-select previously chosen cuisines in the form
    search_form.cuisines.data = cuisines_selected
    vegetarian_only = request.args.get('vegetarian_only', '')
    
    # BUILD QUERY
    restaurant_query = Restaurant.query
    
    if query:
        restaurant_query = restaurant_query.filter(Restaurant.name.ilike(f'%{query}%'))
    
    if location:
        restaurant_query = restaurant_query.filter(Restaurant.location.ilike(f'%{location}%'))
    
    # We will filter by cuisines after fetching, due to JSON storage
    
    # GET RESTAURANTS
    restaurants = restaurant_query.all()
    # Filter by selected cuisines (match any)
    if cuisines_selected:
        sel = set([c for c in cuisines_selected if c])
        if sel:
            restaurants = [r for r in restaurants if sel.intersection(set(r.get_cuisines()))]
    
    # IF VEGETARIAN FILTER IS APPLIED, FURTHER FILTER RESTAURANTS WITH VEGETARIAN OPTIONS
    if vegetarian_only:
        restaurants = [r for r in restaurants if any(item.is_vegetarian for item in r.menu_items)]
    
    return render_template('customer/restaurants.html', 
                           restaurants=restaurants, 
                           search_form=search_form,
                           query=query,
                           location=location,
                           cuisines=cuisines_selected,
                           vegetarian_only=vegetarian_only)

@bp.route('/restaurant/<int:id>')
@login_required
@customer_required
def restaurant_detail(id):
    """
    RESTAURANT DETAIL ROUTE
    """
    restaurant = Restaurant.query.get_or_404(id)
    
    # GET MENU GROUPED BY CATEGORY
    menu_by_category = restaurant.get_menu_by_category()
    
    # CHECK IF RESTAURANT IS IN FAVORITES
    is_favorite = current_user.customer_profile.is_favorite(restaurant.id)
    
    # GET ORDER FEEDBACK FOR THIS RESTAURANT
    from app.models.feedback import Feedback
    feedback_list = Feedback.query.filter_by(restaurant_id=restaurant.id).order_by(Feedback.created_at.desc()).all()
    
    # CHECK IF USER HAS ORDERED FROM THIS RESTAURANT
    has_ordered = Order.query.filter_by(
        customer_id=current_user.customer_profile.id,
        restaurant_id=restaurant.id,
        status=STATUS_COMPLETED  # Only completed orders count
    ).first() is not None
    
    return render_template('customer/restaurant_detail.html', 
                           restaurant=restaurant,
                           menu_by_category=menu_by_category,
                           is_favorite=is_favorite,
                           reviews=feedback_list,
                           has_ordered=has_ordered)

@bp.route('/toggle_favorite/<int:restaurant_id>')
@login_required
@customer_required
def toggle_favorite(restaurant_id):
    """
    TOGGLE FAVORITE RESTAURANT ROUTE
    """
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    if current_user.customer_profile.is_favorite(restaurant_id):
        current_user.customer_profile.remove_from_favorites(restaurant_id)
        flash(f"'{restaurant.name}' HAS BEEN REMOVED FROM YOUR FAVORITES.", "info")
    else:
        current_user.customer_profile.add_to_favorites(restaurant_id)
        flash(f"'{restaurant.name}' HAS BEEN ADDED TO YOUR FAVORITES.", "success")
    
    db.session.commit()
    return redirect(url_for('customer.restaurant_detail', id=restaurant_id))

@bp.route('/cart', methods=['GET', 'POST'])
@login_required
@customer_required
def cart():
    """
    SHOPPING CART ROUTE
    """
    # GET CART FROM SESSION OR INITIALIZE
    cart = session.get('cart', {})
    cart_items = []
    restaurant_name = None
    restaurant_id = None
    total = 0
    
    if cart:
        # GET MENU ITEMS IN CART
        item_ids = [int(id) for id in cart.keys()]
        menu_items = MenuItem.query.filter(MenuItem.id.in_(item_ids)).all()
        
        for item in menu_items:
            quantity = int(cart[str(item.id)])
            subtotal = item.price * quantity
            total += subtotal
            
            cart_items.append({
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'quantity': quantity,
                'subtotal': subtotal
            })
            
            if restaurant_id is None:
                restaurant_id = item.restaurant_id
                restaurant = Restaurant.query.get(restaurant_id)
                restaurant_name = restaurant.name
    
    if request.method == 'POST':
        # PLACE ORDER
        if not cart_items:
            flash("YOUR CART IS EMPTY.", "warning")
            return redirect(url_for('customer.cart'))
        
        # CREATE ORDER
        order = Order(
            customer_id=current_user.customer_profile.id,
            restaurant_id=restaurant_id,
            status=STATUS_PENDING,
            total_amount=total
        )
        db.session.add(order)
        db.session.flush()  # TO GET ORDER ID
        
        # CREATE ORDER ITEMS
        for item in cart_items:
            menu_item = MenuItem.query.get(item['id'])
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item['id'],
                quantity=item['quantity'],
                price=menu_item.price
            )
            db.session.add(order_item)
            
            # UPDATE TIMES ORDERED TODAY COUNT
            menu_item.times_ordered_today += item['quantity']
        
        db.session.commit()
        
        # CLEAR CART
        session['cart'] = {}
        
        logger.info(f"Order #{order.id} placed successfully by {current_user.username}")
        flash("YOUR ORDER HAS BEEN PLACED SUCCESSFULLY!", "success")
        return redirect(url_for('customer.order_detail', id=order.id))
    
    return render_template('customer/cart.html', 
                           cart_items=cart_items,
                           restaurant_name=restaurant_name,
                           restaurant_id=restaurant_id,
                           total=total)

@bp.route('/add_to_cart/<int:item_id>')
@login_required
@customer_required
def add_to_cart(item_id):
    """
    ADD ITEM TO CART ROUTE
    """
    menu_item = MenuItem.query.get_or_404(item_id)
    restaurant_id = menu_item.restaurant_id
    quantity = int(request.args.get('quantity', 1))
    
    # INITIALIZE CART IF NOT PRESENT
    if 'cart' not in session:
        session['cart'] = {}
    
    # CHECK IF CART IS EMPTY OR FROM SAME RESTAURANT
    if session['cart'] and any(MenuItem.query.get(int(id)).restaurant_id != restaurant_id for id in session['cart']):
        flash("YOU CAN ONLY ORDER FROM ONE RESTAURANT AT A TIME. PLEASE CLEAR YOUR CART FIRST.", "warning")
        return redirect(url_for('customer.restaurant_detail', id=restaurant_id))
    
    # ADD OR UPDATE CART
    if str(item_id) in session['cart']:
        session['cart'][str(item_id)] = session['cart'][str(item_id)] + quantity
    else:
        session['cart'][str(item_id)] = quantity
    
    session.modified = True
    
    flash(f"'{menu_item.name}' ADDED TO YOUR CART.", "success")
    return redirect(url_for('customer.restaurant_detail', id=restaurant_id))

@bp.route('/update_cart_item/<int:item_id>', methods=['POST'])
@login_required
@customer_required
def update_cart_item(item_id):
    """
    UPDATE CART ITEM QUANTITY ROUTE
    """
    quantity = int(request.form.get('quantity', 1))
    
    # UPDATE QUANTITY OR REMOVE IF ZERO
    if quantity > 0:
        session['cart'][str(item_id)] = quantity
    else:
        session['cart'].pop(str(item_id), None)
    
    session.modified = True
    
    flash("YOUR CART HAS BEEN UPDATED.", "info")
    return redirect(url_for('customer.cart'))

@bp.route('/clear_cart')
@login_required
@customer_required
def clear_cart():
    """
    CLEAR CART ROUTE
    """
    session['cart'] = {}
    session.modified = True
    
    flash("YOUR CART HAS BEEN CLEARED.", "info")
    return redirect(url_for('customer.cart'))

@bp.route('/orders')
@login_required
@customer_required
def orders():
    """
    ORDER HISTORY ROUTE
    """
    # GET QUERY PARAMETERS FOR SEARCH/FILTER
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    # BUILD QUERY
    orders_query = Order.query.filter_by(customer_id=current_user.customer_profile.id)
    
    if status_filter:
        orders_query = orders_query.filter(Order.status == status_filter)
    
    if search_query:
        # SEARCH BY ORDER ID OR RESTAURANT NAME
        orders_query = orders_query.join(Restaurant).filter(
            or_(
                Order.id.ilike(f'%{search_query}%'),
                Restaurant.name.ilike(f'%{search_query}%')
            )
        )
    
    # GET ORDERS SORTED BY DATE (NEWEST FIRST)
    orders = orders_query.order_by(Order.created_at.desc()).all()
    
    # PRE-LOAD FEEDBACK FOR EACH ORDER TO AVOID TEMPLATE ERRORS
    for order in orders:
        if order.feedback.count() > 0:
            # Force loading of feedback
            _ = list(order.feedback)
    
    return render_template('customer/orders.html', 
                           orders=orders,
                           search_query=search_query,
                           status_filter=status_filter)

@bp.route('/order/<int:id>', methods=['GET', 'POST'])
@login_required
@customer_required
def order_detail(id):
    """
    ORDER DETAIL ROUTE WITH FEEDBACK SUBMISSION FOR COMPLETED ORDERS
    """
    order = Order.query.get_or_404(id)
    
    # ENSURE ORDER BELONGS TO CURRENT USER
    if order.customer_id != current_user.customer_profile.id:
        abort(403)
    
    # GET EXISTING FEEDBACK IF ANY
    existing_feedback = Feedback.query.filter_by(order_id=order.id).first()
    
    # CHECK IF ORDER IS COMPLETED AND CAN RECEIVE FEEDBACK
    can_give_feedback = order.status == STATUS_COMPLETED and not existing_feedback
    
    # ALWAYS CREATE A FEEDBACK FORM
    feedback_form = OrderFeedbackForm()
    
    # HANDLE FEEDBACK SUBMISSION IF CAN GIVE FEEDBACK
    if can_give_feedback:
        
        if request.method == 'POST':
            # Get data directly from the form
            rating = request.form.get('rating', '5')
            message = request.form.get('message', '')
            
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    rating = 5  # Default to 5 if out of range
            except (ValueError, TypeError):
                rating = 5  # Default to 5 if conversion error
            
            # Message is optional, set to empty string if not provided
            message = message.strip() if message else ""
                
            # Double-check if feedback wasn't submitted by another request while this one was processing
            check_existing = Feedback.query.filter_by(order_id=order.id).first()
            if check_existing:
                flash("Feedback has already been submitted for this order.", "info")
                return redirect(url_for('customer.order_detail', id=order.id))
                
            feedback = Feedback(
                order_id=order.id,
                customer_id=current_user.customer_profile.id,
                restaurant_id=order.restaurant_id,
                rating=rating,
                message=message
            )
            
            db.session.add(feedback)
            db.session.commit()
            
            flash("YOUR FEEDBACK HAS BEEN SUBMITTED. THANK YOU!", "success")
            return redirect(url_for('customer.order_detail', id=order.id))
    
    return render_template('customer/order_detail.html', 
                          order=order,
                          can_give_feedback=can_give_feedback,
                          feedback_form=feedback_form,
                          existing_feedback=existing_feedback)

# Review route removed - now using only order-specific feedback


def get_recommendations(customer):
    """
    GET RECOMMENDED RESTAURANTS BASED ON CUSTOMER PREFERENCES AND HISTORY
    """
    recommendations = []
    
    # GET CUSTOMER PREFERENCES
    preferences = customer.get_preferences()
    favorite_cuisines = preferences.get('favorite_cuisines', []) if preferences else []
    dietary_restrictions = customer.get_dietary_restrictions()
    
    # GET PREVIOUSLY ORDERED RESTAURANTS
    ordered_restaurant_ids = db.session.query(Restaurant.id).join(Order).filter(
        Order.customer_id == customer.id
    ).distinct().all()
    ordered_restaurant_ids = [r[0] for r in ordered_restaurant_ids]
    
    # FIND RESTAURANTS THAT MATCH CUSTOMER PREFERENCES (match-any on cuisines list)
    if favorite_cuisines:
        # Start with candidates not already ordered from
        candidate_query = Restaurant.query
        if ordered_restaurant_ids:
            candidate_query = candidate_query.filter(~Restaurant.id.in_(ordered_restaurant_ids))
        candidates = candidate_query.all()
        favorite_set = set(favorite_cuisines)
        cuisine_recommendations = [r for r in candidates if favorite_set.intersection(set(r.get_cuisines()))]
        recommendations.extend(cuisine_recommendations)
    
    # IF VEGETARIAN IS IN PREFERENCES, FIND RESTAURANTS WITH VEGETARIAN OPTIONS
    if 'vegetarian' in dietary_restrictions:
        veg_restaurants = Restaurant.query.join(MenuItem).filter(
            MenuItem.is_vegetarian == True,
            ~Restaurant.id.in_([r.id for r in recommendations]),
            ~Restaurant.id.in_(ordered_restaurant_ids) if ordered_restaurant_ids else True
        ).distinct().all()
        recommendations.extend(veg_restaurants)
    
    # LIMIT TO 5 RECOMMENDATIONS
    return recommendations[:5]
