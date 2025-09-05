"""
CUSTOMER CONTROLLER FOR CUSTOMER FEATURES
"""

import logging
import json
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, abort, session
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app import db
from app.models import User, Customer, Restaurant, MenuItem, Order, OrderItem, Feedback
from app.models.dish_rating import DishRating
from app.models import STATUS_COMPLETED
from app.models import STATUS_PENDING, STATUS_CONFIRMED, STATUS_PREPARING, STATUS_READY, STATUS_COMPLETED
from app.forms.customer_forms import ProfileUpdateForm, PreferencesForm, OrderFeedbackForm, SearchForm, DishRatingForm
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
    apply_dietary_preferences = request.args.get('apply_dietary_preferences', '') in ['on', 'y', 'yes', 'true']
    
    # Pre-select previously chosen cuisines in the form
    search_form.cuisines.data = cuisines_selected
    # Pre-select dietary preferences checkbox if it was checked
    search_form.apply_dietary_preferences.data = apply_dietary_preferences
    
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
    
    # APPLY DIETARY FILTERS WHEN USER CHECKS THE PREFERENCE BOX
    if apply_dietary_preferences:
        customer_dietary_restrictions = current_user.customer_profile.get_dietary_restrictions()
        if customer_dietary_restrictions:
            # Filter restaurants that have menu items matching user's dietary preferences
            filtered_restaurants = []
            for restaurant in restaurants:
                has_matching_items = False
                
                # Check if restaurant has items matching any of the user's dietary preferences
                for item in restaurant.menu_items:
                    if 'vegetarian' in customer_dietary_restrictions and item.is_vegetarian:
                        has_matching_items = True
                        break
                    elif 'vegan' in customer_dietary_restrictions and item.is_vegan:
                        has_matching_items = True
                        break
                    elif 'guilt_free' in customer_dietary_restrictions and item.is_guilt_free:
                        has_matching_items = True
                        break
                
                if has_matching_items:
                    filtered_restaurants.append(restaurant)
            
            restaurants = filtered_restaurants
    
    # ADD FAVORITE STATUS TO EACH RESTAURANT
    for restaurant in restaurants:
        restaurant.is_favorite = current_user.customer_profile.is_favorite(restaurant.id)
    
    return render_template('customer/restaurants.html',
                           restaurants=restaurants,
                           search_form=search_form,
                           query=query,
                           location=location,
                           cuisines=cuisines_selected,
                           apply_dietary_preferences=apply_dietary_preferences)

@bp.route('/restaurant/<int:id>')
@login_required
@customer_required
def restaurant_detail(id):
    """
    RESTAURANT DETAIL ROUTE
    """
    restaurant = Restaurant.query.get_or_404(id)
    
    # GET FILTER PARAMETERS
    search_query = request.args.get('search', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    category_filter = request.args.get('category', '')
    apply_dietary_preferences = request.args.get('apply_dietary_preferences', '') in ['on', 'y', 'yes', 'true']
    
    # GET ALL MENU ITEMS FOR THIS RESTAURANT
    menu_items_query = MenuItem.query.filter_by(restaurant_id=restaurant.id)
    
    # APPLY SEARCH FILTER
    if search_query:
        menu_items_query = menu_items_query.filter(
            MenuItem.name.ilike(f'%{search_query}%') |
            MenuItem.description.ilike(f'%{search_query}%')
        )
    
    # APPLY PRICE FILTER
    if min_price is not None:
        menu_items_query = menu_items_query.filter(MenuItem.price >= min_price)
    if max_price is not None:
        menu_items_query = menu_items_query.filter(MenuItem.price <= max_price)
    
    # APPLY CATEGORY FILTER
    if category_filter:
        menu_items_query = menu_items_query.filter(MenuItem.category == category_filter)
    
    # APPLY DIETARY FILTERS WHEN USER CHECKS THE PREFERENCE BOX
    if apply_dietary_preferences:
        customer_dietary_restrictions = current_user.customer_profile.get_dietary_restrictions()
        if customer_dietary_restrictions:
            # Build filter conditions based on user's dietary preferences
            filter_conditions = []
            
            if 'vegetarian' in customer_dietary_restrictions:
                filter_conditions.append(MenuItem.is_vegetarian == True)
            if 'vegan' in customer_dietary_restrictions:
                filter_conditions.append(MenuItem.is_vegan == True)
            if 'guilt_free' in customer_dietary_restrictions:
                filter_conditions.append(MenuItem.is_guilt_free == True)
            
            # Apply the filters - show items that match ANY of the user's dietary preferences
            if filter_conditions:
                from sqlalchemy import or_
                menu_items_query = menu_items_query.filter(or_(*filter_conditions))
    
    # GET FILTERED MENU ITEMS
    filtered_menu_items = menu_items_query.all()
    
    # GROUP BY CATEGORY
    menu_by_category = {}
    for item in filtered_menu_items:
        if item.category not in menu_by_category:
            menu_by_category[item.category] = []
        menu_by_category[item.category].append(item)
    
    # GET ALL CATEGORIES FOR FILTER DROPDOWN
    all_categories = db.session.query(MenuItem.category).filter_by(restaurant_id=restaurant.id).distinct().all()
    all_categories = [cat[0] for cat in all_categories if cat[0]]
    
    # GET PRICE RANGE FOR SLIDER
    price_range = db.session.query(
        db.func.min(MenuItem.price),
        db.func.max(MenuItem.price)
    ).filter_by(restaurant_id=restaurant.id).first()
    
    min_menu_price = price_range[0] if price_range[0] else 0
    max_menu_price = price_range[1] if price_range[1] else 1000
    
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
    
    # GET RECOMMENDED DISHES FOR THIS RESTAURANT
    recommended_dishes = get_recommended_dishes(current_user.customer_profile, restaurant.id)
    
    return render_template('customer/restaurant_detail.html', 
                           restaurant=restaurant,
                           menu_by_category=menu_by_category,
                           is_favorite=is_favorite,
                           recommended_dishes=recommended_dishes,
                           reviews=feedback_list,
                           has_ordered=has_ordered,
                           search_query=search_query,
                           min_price=min_price,
                           max_price=max_price,
                           category_filter=category_filter,
                           apply_dietary_preferences=apply_dietary_preferences,
                           all_categories=all_categories,
                           min_menu_price=min_menu_price,
                           max_menu_price=max_menu_price)

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
            
            # UPDATE TIMES ORDERED TODAY COUNT WITH AUTOMATIC DAILY RESET
            menu_item.increment_daily_order_count(item['quantity'])
        
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
        message = "YOU CAN ONLY ORDER FROM ONE RESTAURANT AT A TIME. PLEASE CLEAR YOUR CART FIRST."
        # If AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.best == 'application/json':
            return current_app.response_class(
                response=json.dumps({
                    'ok': False,
                    'message': message,
                    'cart_count': len(session.get('cart', {}))
                }),
                status=400,
                mimetype='application/json'
            )
        flash(message, "warning")
        return redirect(url_for('customer.restaurant_detail', id=restaurant_id))
    
    # ADD OR UPDATE CART
    if str(item_id) in session['cart']:
        session['cart'][str(item_id)] = session['cart'][str(item_id)] + quantity
    else:
        session['cart'][str(item_id)] = quantity
    
    session.modified = True
    
    # For AJAX requests, return JSON payload instead of redirect
    success_message = f"'{menu_item.name}' ADDED TO YOUR CART."
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.best == 'application/json':
        return current_app.response_class(
            response=json.dumps({
                'ok': True,
                'message': success_message,
                'cart_count': len(session.get('cart', {})),
                'restaurant_id': restaurant_id,
                'item_id': item_id,
                'quantity': session['cart'][str(item_id)]
            }),
            status=200,
            mimetype='application/json'
        )
    flash(success_message, "success")
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
    
    # GET EXISTING DISH RATINGS IF ANY
    existing_dish_ratings = DishRating.query.filter_by(order_id=order.id).all()
    existing_dish_ratings_dict = {rating.menu_item_id: rating.rating for rating in existing_dish_ratings}
    
    # CHECK IF ORDER IS COMPLETED AND CAN RECEIVE FEEDBACK
    can_give_feedback = order.status == STATUS_COMPLETED and not existing_feedback
    can_rate_dishes = order.status == STATUS_COMPLETED and len(existing_dish_ratings) == 0
    
    # ALWAYS CREATE A FEEDBACK FORM
    feedback_form = OrderFeedbackForm()
    
    # CREATE DISH RATING FORM
    dish_rating_form = DishRatingForm(order_items=order.items)
    
    # HANDLE FEEDBACK SUBMISSION IF CAN GIVE FEEDBACK
    if can_give_feedback:
        
        if request.method == 'POST':
            # Check if this is dish rating submission
            if 'dish_rating_submit' in request.form:
                # Handle dish ratings
                dish_ratings_submitted = []
                for item in order.items:
                    rating_key = f'dish_rating_{item.menu_item_id}'
                    rating_value = request.form.get(rating_key, '5')
                    
                    try:
                        rating_value = int(rating_value)
                        if rating_value < 1 or rating_value > 5:
                            rating_value = 5
                    except (ValueError, TypeError):
                        rating_value = 5
                    
                    dish_ratings_submitted.append({
                        'menu_item_id': item.menu_item_id,
                        'rating': rating_value
                    })
                
                # Check if dish ratings already exist
                existing_dish_ratings_check = DishRating.query.filter_by(order_id=order.id).first()
                if existing_dish_ratings_check:
                    flash("Dish ratings have already been submitted for this order.", "info")
                    return redirect(url_for('customer.order_detail', id=order.id))
                
                # Save dish ratings
                for dish_rating_data in dish_ratings_submitted:
                    dish_rating = DishRating(
                        order_id=order.id,
                        customer_id=current_user.customer_profile.id,
                        restaurant_id=order.restaurant_id,
                        menu_item_id=dish_rating_data['menu_item_id'],
                        rating=dish_rating_data['rating']
                    )
                    db.session.add(dish_rating)
                
                db.session.commit()
                flash("YOUR DISH RATINGS HAVE BEEN SUBMITTED. THANK YOU!", "success")
                return redirect(url_for('customer.order_detail', id=order.id))
            
            else:
                # Handle order feedback
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
                          can_rate_dishes=can_rate_dishes,
                          feedback_form=feedback_form,
                          dish_rating_form=dish_rating_form,
                          existing_feedback=existing_feedback,
                          existing_dish_ratings=existing_dish_ratings_dict)

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
    
    # FIND RESTAURANTS WITH ITEMS MATCHING DIETARY PREFERENCES (for recommendations only)
    if dietary_restrictions:
        from sqlalchemy import or_
        dietary_conditions = []
        
        if 'vegetarian' in dietary_restrictions:
            dietary_conditions.append(MenuItem.is_vegetarian == True)
        if 'vegan' in dietary_restrictions:
            dietary_conditions.append(MenuItem.is_vegan == True)
        if 'guilt_free' in dietary_restrictions:
            dietary_conditions.append(MenuItem.is_guilt_free == True)
        
        if dietary_conditions:
            dietary_restaurants = Restaurant.query.join(MenuItem).filter(
                or_(*dietary_conditions),
                ~Restaurant.id.in_([r.id for r in recommendations]),
                ~Restaurant.id.in_(ordered_restaurant_ids) if ordered_restaurant_ids else True
            ).distinct().all()
            recommendations.extend(dietary_restaurants)
    
    # LIMIT TO 5 RECOMMENDATIONS
    return recommendations[:5]

def get_recommended_dishes(customer, restaurant_id):
    """
    GET RECOMMENDED DISHES BASED ON CUSTOMER PREFERENCES AND ORDER HISTORY
    Returns top 3 dishes that customer hasn't ordered before, sorted by rating
    """
    # GET CUSTOMER PREFERENCES
    preferences = customer.get_preferences()
    favorite_cuisines = preferences.get('favorite_cuisines', []) if preferences else []
    dietary_restrictions = customer.get_dietary_restrictions()
    
    # GET PREVIOUSLY ORDERED MENU ITEMS BY THIS CUSTOMER
    ordered_menu_item_ids = db.session.query(OrderItem.menu_item_id).join(Order).filter(
        Order.customer_id == customer.id,
        Order.status == STATUS_COMPLETED
    ).distinct().all()
    ordered_menu_item_ids = [item[0] for item in ordered_menu_item_ids]
    
    # BUILD QUERY FOR RECOMMENDED DISHES
    from sqlalchemy import func, or_
    
    # Start with dishes from this restaurant that customer hasn't ordered
    recommended_query = MenuItem.query.filter_by(restaurant_id=restaurant_id)
    
    # Exclude previously ordered items
    if ordered_menu_item_ids:
        recommended_query = recommended_query.filter(~MenuItem.id.in_(ordered_menu_item_ids))
    
    # Apply dietary restrictions if user has them
    if dietary_restrictions:
        dietary_conditions = []
        
        if 'vegetarian' in dietary_restrictions:
            dietary_conditions.append(MenuItem.is_vegetarian == True)
        if 'vegan' in dietary_restrictions:
            dietary_conditions.append(MenuItem.is_vegan == True)
        if 'guilt_free' in dietary_restrictions:
            dietary_conditions.append(MenuItem.is_guilt_free == True)
        
        if dietary_conditions:
            recommended_query = recommended_query.filter(or_(*dietary_conditions))
    
    # Get dishes with ratings, ordered by average rating (highest first)
    # Only include dishes that have at least one rating
    recommended_dishes = recommended_query.join(DishRating).group_by(
        MenuItem.id
    ).order_by(
        func.avg(DishRating.rating).desc()
    ).limit(3).all()
    
    return recommended_dishes