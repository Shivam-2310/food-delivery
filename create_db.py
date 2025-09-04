"""
DATABASE INITIALIZATION SCRIPT
"""
from app import create_app, db
from app.models import User, Customer, RestaurantOwner, Restaurant, MenuItem, Order, OrderItem, Feedback
from app.models import ROLE_CUSTOMER, ROLE_OWNER, STATUS_COMPLETED
from datetime import datetime, timedelta

# CREATE APP CONTEXT
app = create_app()
with app.app_context():
    # CREATE ALL TABLES
    db.create_all()
    print("DATABASE TABLES CREATED SUCCESSFULLY!")
    
    # CREATE DEMO USERS
    if User.query.filter_by(username='customer').first() is None:
        customer_user = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        customer_user.set_password('password123')
        db.session.add(customer_user)
        db.session.flush()  # GET ID
        
        # CREATE CUSTOMER PROFILE
        customer = Customer(
            user_id=customer_user.id,
            name='Rahul Sharma',
            address='123 Connaught Place, New Delhi, India',
            phone='9876543210'
        )
        db.session.add(customer)
        
    if User.query.filter_by(username='owner').first() is None:
        owner_user = User(username='owner', email='owner@example.com', role=ROLE_OWNER)
        owner_user.set_password('password123')
        db.session.add(owner_user)
        db.session.flush()  # GET ID
        
        # CREATE OWNER PROFILE
        owner = RestaurantOwner(
            user_id=owner_user.id,
            name='Priya Patel',
            phone='8765432109'
        )
        db.session.add(owner)
        db.session.flush()  # GET ID
        
        # CREATE SAMPLE RESTAURANT
        restaurant = Restaurant(
            owner_id=owner.id,
            name='Spice Junction',
            description='An authentic restaurant offering a variety of delicious Indian cuisines.',
            location='45 Chandni Chowk, Old Delhi, India'
        )
        restaurant.set_cuisines(['North Indian'])
        db.session.add(restaurant)
        db.session.flush()  # GET ID
        
        # CREATE SAMPLE MENU ITEMS
        menu_items = [
            MenuItem(
                restaurant_id=restaurant.id,
                name='Paneer Butter Masala',
                description='Cottage cheese cubes in rich tomato and butter gravy with Indian spices.',
                price=299,
                category='main_course',
                is_vegetarian=True
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                name='Chicken Biryani',
                description='Fragrant basmati rice cooked with tender chicken pieces and aromatic spices.',
                price=349,
                category='main_course',
                is_vegetarian=False
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                name='Garlic Naan',
                description='Soft bread with garlic flavor, baked in tandoor.',
                price=80,
                category='appetizer',
                is_vegetarian=True,
                is_special=True
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                name='Gulab Jamun',
                description='Sweet milk-solid based dessert soaked in sugar syrup.',
                price=120,
                category='dessert',
                is_vegetarian=True,
                is_deal_of_day=True
            )
        ]
        
        for item in menu_items:
            db.session.add(item)
    
        # CREATE A COMPLETED ORDER FOR TESTING FEEDBACK
        completed_order = Order(
            customer_id=Customer.query.first().id,
            restaurant_id=Restaurant.query.first().id,
            status=STATUS_COMPLETED,
            total_amount=429,  # Chicken Biryani + Garlic Naan
            created_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(completed_order)
        db.session.flush()
        
        # ADD ORDER ITEMS
        biryani = MenuItem.query.filter_by(name='Chicken Biryani').first()
        naan = MenuItem.query.filter_by(name='Garlic Naan').first()
        
        if biryani and naan:
            order_items = [
                OrderItem(
                    order_id=completed_order.id,
                    menu_item_id=biryani.id,
                    quantity=1,
                    price=biryani.price
                ),
                OrderItem(
                    order_id=completed_order.id,
                    menu_item_id=naan.id,
                    quantity=1,
                    price=naan.price
                )
            ]
            for item in order_items:
                db.session.add(item)
            
            # ADD FEEDBACK FOR THE COMPLETED ORDER
            feedback = Feedback(
                order_id=completed_order.id,
                customer_id=Customer.query.first().id,
                restaurant_id=Restaurant.query.first().id,
                rating=4,
                message="The food was delicious, especially the Chicken Biryani. Delivery was on time and the food was still hot. Will order again!",
                is_resolved=True,
                response="Thank you for your kind feedback! We're glad you enjoyed our Biryani. Looking forward to serving you again soon!"
            )
            db.session.add(feedback)
    
    # COMMIT ALL CHANGES
    db.session.commit()
    print("DEMO DATA SEEDED SUCCESSFULLY!")
