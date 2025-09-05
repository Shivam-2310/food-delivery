"""Simple script to seed user data."""

from app import create_app, db
from app.models import Customer, RestaurantOwner, User, ROLE_CUSTOMER, ROLE_OWNER

def seed_users():
    """Seed the database with demo users."""
    app = create_app()
    with app.app_context():
        # Create customer1
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
            print("Created customer1: Rahul Sharma")

        # Create customer2
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
            print("Created customer2: Anita Verma")

        # Create owner1
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
            print("Created owner1: Priya Patel")

        # Create owner2
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
            print("Created owner2: Arjun Mehta")

        db.session.commit()
        print("DEMO DATA SEEDED SUCCESSFULLY: 2 customers and 2 owners created. No restaurants added.")

if __name__ == '__main__':
    seed_users()
