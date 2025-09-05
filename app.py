"""JustEat main application file."""
from app import create_app, db
from app.models import Customer, RestaurantOwner, User
from app.models import ROLE_CUSTOMER, ROLE_OWNER

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Make objects available in Flask shell."""
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
    """Initialize database tables."""
    db.create_all()
    print("DATABASE TABLES CREATED")

@app.cli.command("seed-data")
def seed_data():
    """Seed the database with initial data."""
    # Create exactly two customers and two owners. No restaurants or menu items.
    # Customers
    if User.query.filter_by(username='customer1').first() is None:
        customer_user1 = User(username='customer1', email='customer1@example.com', role=ROLE_CUSTOMER)
        customer_user1.set_password('password123')
        db.session.add(customer_user1)
        db.session.flush()
        customer1 = Customer(
            user_id=customer_user1.id,
            name='Rahul Sharma',
            address='123 Connaught Place, New Delhi, India',
            phone='9876543210'
        )
        db.session.add(customer1)

    if User.query.filter_by(username='customer2').first() is None:
        customer_user2 = User(username='customer2', email='customer2@example.com', role=ROLE_CUSTOMER)
        customer_user2.set_password('password123')
        db.session.add(customer_user2)
        db.session.flush()
        customer2 = Customer(
            user_id=customer_user2.id,
            name='Anita Verma',
            address='55 Park Street, Kolkata, India',
            phone='9898989898'
        )
        db.session.add(customer2)

    # Owners
    if User.query.filter_by(username='owner1').first() is None:
        owner_user1 = User(username='owner1', email='owner1@example.com', role=ROLE_OWNER)
        owner_user1.set_password('password123')
        db.session.add(owner_user1)
        db.session.flush()
        owner1 = RestaurantOwner(
            user_id=owner_user1.id,
            name='Priya Patel',
            phone='8765432109'
        )
        db.session.add(owner1)

    if User.query.filter_by(username='owner2').first() is None:
        owner_user2 = User(username='owner2', email='owner2@example.com', role=ROLE_OWNER)
        owner_user2.set_password('password123')
        db.session.add(owner_user2)
        db.session.flush()
        owner2 = RestaurantOwner(
            user_id=owner_user2.id,
            name='Arjun Mehta',
            phone='9123456780'
        )
        db.session.add(owner2)

    db.session.commit()
    print("DEMO DATA SEEDED SUCCESSFULLY: 2 customers and 2 owners created. No restaurants added.")

if __name__ == '__main__':
    app.run(debug=True)
