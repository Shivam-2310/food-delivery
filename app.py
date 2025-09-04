"""
JUSTEAT MAIN APPLICATION FILE
"""
from app import create_app, db
from app.models import User, Customer, RestaurantOwner, Restaurant, MenuItem, Order
from app.models import ROLE_CUSTOMER, ROLE_OWNER

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    MAKE OBJECTS AVAILABLE IN FLASK SHELL
    """
    return {
        'db': db,
        'User': User,
        'Customer': Customer,
        'RestaurantOwner': RestaurantOwner,
        'Restaurant': Restaurant,
        'MenuItem': MenuItem,
        'Order': Order,
        'ROLE_CUSTOMER': ROLE_CUSTOMER,
        'ROLE_OWNER': ROLE_OWNER
    }

@app.cli.command("init-db")
def init_db():
    """
    INITIALIZE DATABASE TABLES
    """
    db.create_all()
    print("DATABASE TABLES CREATED")

@app.cli.command("seed-data")
def seed_data():
    """
    SEED THE DATABASE WITH INITIAL DATA
    """
    # CREATE DEMO USERS
    if User.query.filter_by(username='customer').first() is None:
        customer_user = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        customer_user.set_password('password123')
        db.session.add(customer_user)
        db.session.flush()  # GET ID
        
        # CREATE CUSTOMER PROFILE
        customer = Customer(
            user_id=customer_user.id,
            name='Demo Customer',
            address='123 Main St, Anytown, USA',
            phone='555-123-4567'
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
            name='Demo Restaurant Owner',
            phone='555-987-6543'
        )
        db.session.add(owner)
        db.session.flush()  # GET ID
        
        # CREATE SAMPLE RESTAURANT
        restaurant = Restaurant(
            owner_id=owner.id,
            name='Tasty Treats',
            description='A delicious restaurant with a variety of cuisines to satisfy any craving.',
            location='456 Food Ave, Cuisine City, USA'
        )
        restaurant.set_cuisines(['Italian'])
        db.session.add(restaurant)
        db.session.flush()  # GET ID
        
        # CREATE SAMPLE MENU ITEMS
        menu_items = [
            MenuItem(
                restaurant_id=restaurant.id,
                name='Margherita Pizza',
                description='Classic pizza with tomato sauce, mozzarella, and basil.',
                price=12.99,
                category='main_course',
                is_vegetarian=True
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                name='Spaghetti Carbonara',
                description='Pasta with creamy sauce, pancetta, eggs, and parmesan.',
                price=14.99,
                category='main_course',
                is_vegetarian=False
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                name='Garlic Bread',
                description='Crispy bread with garlic butter and herbs.',
                price=4.99,
                category='appetizer',
                is_vegetarian=True,
                is_special=True
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                name='Tiramisu',
                description='Italian coffee-flavored dessert with mascarpone and cocoa.',
                price=6.99,
                category='dessert',
                is_vegetarian=True,
                is_deal_of_day=True
            )
        ]
        
        for item in menu_items:
            db.session.add(item)
    
    db.session.commit()
    print("DEMO DATA SEEDED SUCCESSFULLY")

if __name__ == '__main__':
    app.run(debug=True)
