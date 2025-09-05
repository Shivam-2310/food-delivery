"""Tests for application routes."""

import json
import unittest

from flask import url_for

from app import create_app, db
from app.models import Customer, MenuItem, Restaurant, RestaurantOwner, User
from app.models import ROLE_CUSTOMER, ROLE_OWNER

class TestRoutes(unittest.TestCase):
    """Test cases for application routes."""
    
    def setUp(self):
        """Set up test environment."""
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
        
        # Create test data.
        self._create_test_data()
        
    def tearDown(self):
        """Clean up test environment."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def _create_test_data(self):
        """Create test users and data."""
        # Create customer user.
        customer_user = User(username='customer', email='customer@example.com', role=ROLE_CUSTOMER)
        customer_user.set_password('password123')
        customer_user.set_password('password123')
        db.session.add(customer_user)
        db.session.flush()
        
        customer = Customer(user_id=customer_user.id, name='Test Customer')
        db.session.add(customer)
        
        # Create owner user.
        owner_user = User(username='owner', email='owner@example.com', role=ROLE_OWNER)
        owner_user.set_password('password123')
        owner_user.set_password('password123')
        db.session.add(owner_user)
        db.session.flush()
        
        owner = RestaurantOwner(user_id=owner_user.id, name='Test Owner')
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
        """Helper method to log in."""
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password,
            'role': 'customer' if username == 'customer' else 'owner'
        }, follow_redirects=True)
    
    def test_index_page(self):
        """Test index page."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ORDER DELICIOUS FOOD ONLINE', response.data)
    
    def test_login_page(self):
        """Test login page loads."""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign in to your account', response.data)
    
    def test_login_success_customer(self):
        """Test successful customer login."""
        response = self._login('customer', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN SUCCESSFUL', response.data)
        self.assertIn(b'Welcome back, Test Customer!', response.data)
    
    def test_login_success_owner(self):
        """Test successful owner login."""
        response = self._login('owner', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN SUCCESSFUL', response.data)
    
    def test_login_failure(self):
        """Test failed login."""
        response = self.client.post('/auth/login', data={
            'username': 'customer',
            'password': 'wrongpassword',
            'role': 'customer'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'INVALID USERNAME, PASSWORD OR ROLE', response.data)
    
    def test_customer_dashboard_access(self):
        """Test customer dashboard access control."""
        # Unauthenticated access.
        response = self.client.get('/customer/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign in to your account', response.data)
        
        # Authenticated access.
        self._login('customer', 'password123')
        response = self.client.get('/customer/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back, Test Customer!', response.data)
        self.assertIn(b'Welcome back, Test Customer!', response.data)
    
    def test_owner_dashboard_access(self):
        """Test owner dashboard access control."""
        # Unauthenticated access.
        response = self.client.get('/owner/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign in to your account', response.data)
        
        # Authenticated access.
        self._login('owner', 'password123')
        response = self.client.get('/owner/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Restaurant Owner Dashboard', response.data)
    
    def test_role_based_access(self):
        """Test role-based access control."""
        # Customer trying to access owner routes (forbidden; expect 403).
        self._login('customer', 'password123')
        response = self.client.get('/owner/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 403)
        
        # Owner trying to access customer routes (allowed; expect 200).
        self._login('owner', 'password123')
        response = self.client.get('/customer/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 200)
    
    def test_restaurant_listing(self):
        """Test restaurant listing."""
        self._login('customer', 'password123')
        response = self.client.get('/customer/restaurants')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Restaurant', response.data)
        self.assertIn(b'Italian', response.data)
    
    def test_restaurant_detail(self):
        """Test restaurant detail page."""
        self._login('customer', 'password123')
        
        # Get restaurant ID.
        restaurant = Restaurant.query.filter_by(name='Test Restaurant').first()
        
        response = self.client.get(f'/customer/restaurant/{restaurant.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Restaurant', response.data)
        self.assertIn(b'Pizza', response.data)
        self.assertIn(b'Pasta', response.data)
    
    def test_logout(self):
        """Test logout functionality."""
        self._login('customer', 'password123')
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'YOU HAVE BEEN LOGGED OUT SUCCESSFULLY', response.data)
        
        # Verify dashboard is no longer accessible.
        response = self.client.get('/customer/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign in to your account', response.data)

if __name__ == '__main__':
    unittest.main()
