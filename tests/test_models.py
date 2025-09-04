"""
TESTS FOR DATABASE MODELS
"""

import unittest
from app import create_app, db
from app.models import User, Customer, RestaurantOwner, Restaurant, MenuItem, Review, Order, OrderItem
from app.models import ROLE_CUSTOMER, ROLE_OWNER
import os
import json

class TestModels(unittest.TestCase):
    """
    TEST CASES FOR DATABASE MODELS
    """
    
    def setUp(self):
        """
        SET UP TEST ENVIRONMENT
        """
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """
        CLEAN UP TEST ENVIRONMENT
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """
        TEST USER MODEL CREATION AND PASSWORD HASHING
        """
        user = User(username='testuser', email='test@example.com', role=ROLE_CUSTOMER)
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # RETRIEVE USER
        saved_user = User.query.filter_by(username='testuser').first()
        
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.email, 'test@example.com')
        self.assertEqual(saved_user.role, ROLE_CUSTOMER)
        self.assertTrue(saved_user.check_password('password123'))
        self.assertFalse(saved_user.check_password('wrongpassword'))
        self.assertTrue(saved_user.is_customer())
        self.assertFalse(saved_user.is_owner())
    
    def test_customer_preferences(self):
        """
        TEST CUSTOMER PREFERENCES JSON STORAGE AND RETRIEVAL
        """
        # CREATE USER AND CUSTOMER
        user = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        customer = Customer(user_id=user.id, name='Test Customer')
        db.session.add(customer)
        db.session.commit()
        
        # TEST PREFERENCES
        prefs = {
            'favorite_cuisines': ['Italian', 'Mexican', 'Thai'],
            'favorite_restaurants': [1, 3, 5]
        }
        customer.set_preferences(prefs)
        db.session.commit()
        
        # RETRIEVE AND CHECK
        saved_customer = Customer.query.get(customer.id)
        retrieved_prefs = saved_customer.get_preferences()
        
        self.assertEqual(retrieved_prefs['favorite_cuisines'], ['Italian', 'Mexican', 'Thai'])
        self.assertEqual(retrieved_prefs['favorite_restaurants'], [1, 3, 5])
        
        # TEST DIETARY RESTRICTIONS
        restrictions = ['vegetarian', 'gluten_free']
        customer.set_dietary_restrictions(restrictions)
        db.session.commit()
        
        saved_customer = Customer.query.get(customer.id)
        retrieved_restrictions = saved_customer.get_dietary_restrictions()
        
        self.assertEqual(retrieved_restrictions, ['vegetarian', 'gluten_free'])
    
    def test_restaurant_and_menu_items(self):
        """
        TEST RESTAURANT AND MENU ITEMS CREATION AND RELATIONSHIPS
        """
        # CREATE OWNER
        user = User(username='owner', email='owner@example.com', role=ROLE_OWNER)
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        owner = RestaurantOwner(user_id=user.id, name='Test Owner')
        db.session.add(owner)
        db.session.flush()
        
        # CREATE RESTAURANT
        restaurant = Restaurant(
            owner_id=owner.id,
            name='Test Restaurant',
            description='Test Description',
            location='Test Location'
        )
        restaurant.set_cuisines(['Italian'])
        db.session.add(restaurant)
        db.session.flush()
        
        # CREATE MENU ITEMS
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
        
        # RETRIEVE AND CHECK
        saved_restaurant = Restaurant.query.get(restaurant.id)
        self.assertEqual(saved_restaurant.name, 'Test Restaurant')
        self.assertEqual(saved_restaurant.get_cuisines(), ['Italian'])
        
        menu_items = saved_restaurant.menu_items.all()
        self.assertEqual(len(menu_items), 2)
        
        # CHECK MENU BY CATEGORY
        menu_by_category = saved_restaurant.get_menu_by_category()
        self.assertEqual(len(menu_by_category['main_course']), 2)
        
        # CHECK SPECIAL FLAG
        special_items = [item for item in menu_items if item.is_special]
        self.assertEqual(len(special_items), 1)
        self.assertEqual(special_items[0].name, 'Pasta')
    
    def test_order_creation_and_status(self):
        """
        TEST ORDER CREATION AND STATUS UPDATES
        """
        # CREATE CUSTOMER
        user1 = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        user1.set_password('password123')
        db.session.add(user1)
        db.session.flush()
        
        customer = Customer(user_id=user1.id, name='Test Customer')
        db.session.add(customer)
        
        # CREATE OWNER AND RESTAURANT
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
        
        # CREATE MENU ITEM
        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            name='Test Item',
            description='Test Description',
            price=10.99,
            category='main_course'
        )
        db.session.add(menu_item)
        db.session.flush()
        
        # CREATE ORDER
        order = Order(
            customer_id=customer.id,
            restaurant_id=restaurant.id,
            status='pending',
            total_amount=21.98
        )
        db.session.add(order)
        db.session.flush()
        
        # ADD ORDER ITEMS
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=2,
            price=10.99
        )
        db.session.add(order_item)
        db.session.commit()
        
        # RETRIEVE AND CHECK
        saved_order = Order.query.get(order.id)
        self.assertEqual(saved_order.status, 'pending')
        self.assertEqual(saved_order.total_amount, 21.98)
        
        # CHECK ITEM COUNT
        self.assertEqual(saved_order.item_count, 2)
        
        # TEST STATUS UPDATE
        self.assertTrue(saved_order.update_status('confirmed'))
        db.session.commit()
        
        saved_order = Order.query.get(order.id)
        self.assertEqual(saved_order.status, 'confirmed')
        
        # TEST INVALID STATUS
        self.assertFalse(saved_order.update_status('invalid_status'))
    
    def test_review_system(self):
        """
        TEST REVIEW CREATION AND RELATIONSHIPS
        """
        # CREATE CUSTOMER
        user1 = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        user1.set_password('password123')
        db.session.add(user1)
        db.session.flush()
        
        customer = Customer(user_id=user1.id, name='Test Customer')
        db.session.add(customer)
        
        # CREATE OWNER AND RESTAURANT
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
        
        # CREATE MENU ITEM
        menu_item = MenuItem(
            restaurant_id=restaurant.id,
            name='Test Item',
            description='Test Description',
            price=10.99,
            category='main_course'
        )
        db.session.add(menu_item)
        db.session.flush()
        
        # CREATE REVIEWS
        restaurant_review = Review(
            customer_id=customer.id,
            restaurant_id=restaurant.id,
            rating=4,
            comment='Great restaurant!'
        )
        
        menu_item_review = Review(
            customer_id=customer.id,
            restaurant_id=restaurant.id,
            menu_item_id=menu_item.id,
            rating=5,
            comment='Delicious food!'
        )
        
        db.session.add_all([restaurant_review, menu_item_review])
        db.session.commit()
        
        # CHECK RESTAURANT RATING
        saved_restaurant = Restaurant.query.get(restaurant.id)
        self.assertEqual(saved_restaurant.average_rating, 4.5)  # (4+5)/2
        self.assertEqual(saved_restaurant.total_reviews, 2)
        
        # CHECK MENU ITEM RATING
        saved_menu_item = MenuItem.query.get(menu_item.id)
        self.assertEqual(saved_menu_item.average_rating, 5)
        self.assertEqual(saved_menu_item.total_reviews, 1)

if __name__ == '__main__':
    unittest.main()
