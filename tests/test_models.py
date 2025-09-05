"""Tests for database models."""

import json
import os
import unittest

from app import create_app, db
from app.models import (
    Customer,
    MenuItem,
    Order,
    OrderItem,
    Restaurant,
    RestaurantOwner,
    User,
)
from app.models import ROLE_CUSTOMER, ROLE_OWNER

class TestModels(unittest.TestCase):
    """Test cases for database models."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """Test user model creation and password hashing."""
        user = User(username='testuser', email='test@example.com', role=ROLE_CUSTOMER)
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Retrieve user.
        saved_user = User.query.filter_by(username='testuser').first()
        
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.email, 'test@example.com')
        self.assertEqual(saved_user.role, ROLE_CUSTOMER)
        self.assertTrue(saved_user.check_password('password123'))
        self.assertFalse(saved_user.check_password('wrongpassword'))
        self.assertTrue(saved_user.is_customer())
        self.assertFalse(saved_user.is_owner())
    
    def test_customer_preferences(self):
        """Test customer preferences JSON storage and retrieval."""
        # Create user and customer.
        user = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        customer = Customer(user_id=user.id, name='Test Customer')
        db.session.add(customer)
        db.session.commit()
        
        # Test preferences.
        prefs = {
            'favorite_cuisines': ['Italian', 'Mexican', 'Thai'],
            'favorite_restaurants': [1, 3, 5]
        }
        customer.set_preferences(prefs)
        db.session.commit()
        
        # Retrieve and check.
        saved_customer = Customer.query.get(customer.id)
        retrieved_prefs = saved_customer.get_preferences()
        
        self.assertEqual(retrieved_prefs['favorite_cuisines'], ['Italian', 'Mexican', 'Thai'])
        self.assertEqual(retrieved_prefs['favorite_restaurants'], [1, 3, 5])
        
        # Test dietary restrictions.
        restrictions = ['vegetarian', 'gluten_free']
        customer.set_dietary_restrictions(restrictions)
        db.session.commit()
        
        saved_customer = Customer.query.get(customer.id)
        retrieved_restrictions = saved_customer.get_dietary_restrictions()
        
        self.assertEqual(retrieved_restrictions, ['vegetarian', 'gluten_free'])
    
    def test_restaurant_and_menu_items(self):
        """Test restaurant and menu items creation and relationships."""
        # Create owner.
        user = User(username='owner', email='owner@example.com', role=ROLE_OWNER)
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        owner = RestaurantOwner(user_id=user.id, name='Test Owner')
        db.session.add(owner)
        db.session.flush()
        
        # Create restaurant.
        restaurant = Restaurant(
            owner_id=owner.id,
            name='Test Restaurant',
            description='Test Description',
            location='Test Location'
        )
        restaurant.set_cuisines(['Italian'])
        db.session.add(restaurant)
        db.session.flush()
        
        # Create menu items.
        pizza = MenuItem(
            restaurant_id=restaurant.id,
            name='Pizza',
            description='Delicious pizza',
            price=10.99,
            category='main_course',
            is_vegetarian=True
        )
        pasta = MenuItem(
            restaurant_id=restaurant.id,
            name='Pasta',
            description='Tasty pasta',
            price=8.99,
            category='main_course',
            is_vegetarian=True,
            is_special=True
        )
        
        db.session.add_all([pizza, pasta])
        db.session.commit()
        
        # Retrieve and check.
        saved_restaurant = Restaurant.query.get(restaurant.id)
        self.assertEqual(saved_restaurant.name, 'Test Restaurant')
        self.assertEqual(saved_restaurant.get_cuisines(), ['Italian'])
        
        menu_items = saved_restaurant.menu_items.all()
        self.assertEqual(len(menu_items), 2)
        
        # Check menu by category.
        menu_by_category = saved_restaurant.get_menu_by_category()
        self.assertEqual(len(menu_by_category['main_course']), 2)
        
        # Check special flag.
        special_items = [item for item in menu_items if item.is_special]
        self.assertEqual(len(special_items), 1)
        self.assertEqual(special_items[0].name, 'Pasta')
    
    def test_order_creation_and_status(self):
        """Test order creation and status updates."""
        # Create customer.
        user1 = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        user1.set_password('password123')
        db.session.add(user1)
        db.session.flush()
        
        customer = Customer(user_id=user1.id, name='Test Customer')
        db.session.add(customer)
        
        # Create owner and restaurant.
        user2 = User(username='owner', email='owner@example.com', role=ROLE_OWNER)
        user2.set_password('password123')
        db.session.add(user2)
        db.session.flush()
        
        owner = RestaurantOwner(user_id=user2.id, name='Test Owner')
        db.session.add(owner)
        db.session.flush()
        
        restaurant = Restaurant(
            owner_id=owner.id,
            name='Test Restaurant',
            description='Test Description',
            location='Test Location'
        )
        restaurant.set_cuisines(['Italian'])
        db.session.add(restaurant)
        db.session.flush()
        
        # Create menu item.
        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            name='Test Item',
            description='Test Description',
            price=10.99,
            category='main_course'
        )
        db.session.add(menu_item)
        db.session.flush()
        
        # Create order.
        order = Order(
            customer_id=customer.id,
            restaurant_id=restaurant.id,
            status='pending',
            total_amount=21.98
        )
        db.session.add(order)
        db.session.flush()
        
        # Add order items.
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=2,
            price=10.99
        )
        db.session.add(order_item)
        db.session.commit()
        
        # Retrieve and check.
        saved_order = Order.query.get(order.id)
        self.assertEqual(saved_order.status, 'pending')
        self.assertEqual(saved_order.total_amount, 21.98)
        
        # Check item count.
        self.assertEqual(saved_order.item_count, 2)
        
        # Test status update.
        self.assertTrue(saved_order.update_status('confirmed'))
        db.session.commit()
        
        saved_order = Order.query.get(order.id)
        self.assertEqual(saved_order.status, 'confirmed')
        
        # Test invalid status.
        self.assertFalse(saved_order.update_status('invalid_status'))
    

if __name__ == '__main__':
    unittest.main()
