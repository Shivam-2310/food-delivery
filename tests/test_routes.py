"""
TESTS FOR APPLICATION ROUTES
"""

import unittest
from app import create_app, db
from app.models import User, Customer, RestaurantOwner, Restaurant, MenuItem
from app.models import ROLE_CUSTOMER, ROLE_OWNER
import json
from flask import url_for

class TestRoutes(unittest.TestCase):
    """
    TEST CASES FOR APPLICATION ROUTES
    """
    
    def setUp(self):
        """
        SET UP TEST ENVIRONMENT
        """
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SERVER_NAME': 'localhost'
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # CREATE TEST DATA
        self._create_test_data()
        
    def tearDown(self):
        """
        CLEAN UP TEST ENVIRONMENT
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def _create_test_data(self):
        """
        CREATE TEST USERS AND DATA
        """
        # CREATE CUSTOMER USER
        customer_user = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        customer_user.set_password('password123')
        db.session.add(customer_user)
        db.session.flush()
        
        customer = Customer(user_id=customer_user.id, name='Test Customer')
        db.session.add(customer)
        
        # CREATE OWNER USER
        owner_user = User(username='owner', email='owner@example.com', role=ROLE_OWNER)
        owner_user.set_password('password123')
        db.session.add(owner_user)
        db.session.flush()
        
        owner = RestaurantOwner(user_id=owner_user.id, name='Test Owner')
        db.session.add(owner)
        db.session.flush()
        
        # CREATE RESTAURANT
        restaurant = Restaurant(
            owner_id=owner.id,
            name='Test Restaurant',
            description='Test Description',
            location='Test Location',
            cuisine_type='Italian'
        )
        db.session.add(restaurant)
        db.session.flush()
        
        # CREATE MENU ITEMS
        menu_items = [
            MenuItem(
                restaurant_id=restaurant.id,
                name='Pizza',
                description='Delicious pizza',
                price=10.99,
                category='main_course',
                is_vegetarian=True
            ),
            MenuItem(
                restaurant_id=restaurant.id,
                name='Pasta',
                description='Tasty pasta',
                price=8.99,
                category='main_course',
                is_vegetarian=True,
                is_special=True
            )
        ]
        
        db.session.add_all(menu_items)
        db.session.commit()
    
    def _login(self, username, password):
        """
        HELPER METHOD TO LOG IN
        """
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password,
            'role': 'customer' if username == 'customer' else 'owner'
        }, follow_redirects=True)
    
    def test_index_page(self):
        """
        TEST INDEX PAGE
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ORDER DELICIOUS FOOD ONLINE', response.data)
    
    def test_login_page(self):
        """
        TEST LOGIN PAGE LOADS
        """
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN TO JUSTEAT', response.data)
    
    def test_login_success_customer(self):
        """
        TEST SUCCESSFUL CUSTOMER LOGIN
        """
        response = self._login('customer', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN SUCCESSFUL', response.data)
        self.assertIn(b'WELCOME, TEST CUSTOMER', response.data)
    
    def test_login_success_owner(self):
        """
        TEST SUCCESSFUL OWNER LOGIN
        """
        response = self._login('owner', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN SUCCESSFUL', response.data)
    
    def test_login_failure(self):
        """
        TEST FAILED LOGIN
        """
        response = self.client.post('/auth/login', data={
            'username': 'customer',
            'password': 'wrongpassword',
            'role': 'customer'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'INVALID USERNAME, PASSWORD OR ROLE', response.data)
    
    def test_customer_dashboard_access(self):
        """
        TEST CUSTOMER DASHBOARD ACCESS CONTROL
        """
        # UNAUTHENTICATED ACCESS
        response = self.client.get('/customer/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN TO JUSTEAT', response.data)
        
        # AUTHENTICATED ACCESS
        self._login('customer', 'password123')
        response = self.client.get('/customer/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'WELCOME, TEST CUSTOMER', response.data)
    
    def test_owner_dashboard_access(self):
        """
        TEST OWNER DASHBOARD ACCESS CONTROL
        """
        # UNAUTHENTICATED ACCESS
        response = self.client.get('/owner/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN TO JUSTEAT', response.data)
        
        # AUTHENTICATED ACCESS
        self._login('owner', 'password123')
        response = self.client.get('/owner/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Restaurant Management', response.data)
    
    def test_role_based_access(self):
        """
        TEST ROLE-BASED ACCESS CONTROL
        """
        # CUSTOMER TRYING TO ACCESS OWNER ROUTES
        self._login('customer', 'password123')
        response = self.client.get('/owner/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 403)
        
        # OWNER TRYING TO ACCESS CUSTOMER ROUTES
        self._login('owner', 'password123')
        response = self.client.get('/customer/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 403)
    
    def test_restaurant_listing(self):
        """
        TEST RESTAURANT LISTING
        """
        self._login('customer', 'password123')
        response = self.client.get('/customer/restaurants')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Restaurant', response.data)
        self.assertIn(b'Italian', response.data)
    
    def test_restaurant_detail(self):
        """
        TEST RESTAURANT DETAIL PAGE
        """
        self._login('customer', 'password123')
        
        # GET RESTAURANT ID
        restaurant = Restaurant.query.filter_by(name='Test Restaurant').first()
        
        response = self.client.get(f'/customer/restaurant/{restaurant.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Restaurant', response.data)
        self.assertIn(b'Pizza', response.data)
        self.assertIn(b'Pasta', response.data)
    
    def test_logout(self):
        """
        TEST LOGOUT FUNCTIONALITY
        """
        self._login('customer', 'password123')
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'YOU HAVE BEEN LOGGED OUT SUCCESSFULLY', response.data)
        
        # VERIFY DASHBOARD IS NO LONGER ACCESSIBLE
        response = self.client.get('/customer/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN TO JUSTEAT', response.data)

if __name__ == '__main__':
    unittest.main()
