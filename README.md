# JustEat - Food Ordering Application

A comprehensive food ordering platform built with Flask, allowing customers to browse restaurants, place orders, and restaurant owners to manage their menus and orders.

## Features

### Customer Features
- Browse and search for restaurants by location, cuisine, or name
- View restaurant menus with filters for cuisine type, price, etc.
- Place orders with customizable quantities
- Track order status and view order history
- Save preferences including favorite restaurants and dietary restrictions
- Receive personalized recommendations
- Submit ratings and reviews for restaurants and menu items
- Provide feedback on the application experience

### Restaurant Owner Features
- Register restaurants on the platform
- Manage restaurant profile and menu items
- Process and update orders
- Highlight special menu items and deals of the day
- View order statistics and reports

## Tech Stack

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Form Validation**: Flask-WTF

## Project Structure

```
food-ordering-exit-test/
├── app/
│   ├── controllers/      # Route handling logic
│   ├── forms/            # Form definitions and validation 
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── static/           # Static assets (CSS, JS, images)
│   ├── templates/        # Jinja2 templates
│   ├── utils/            # Utility functions
│   └── __init__.py       # Application factory
├── instance/             # Instance-specific data
├── tests/                # Unit tests
├── app.py               # Application entry point
├── create_db.py         # Database initialization script
└── requirements.txt     # Project dependencies
```

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. Clone the repository:
```
git clone https://github.com/yourusername/justeat.git
cd justeat
```

2. Create and activate a virtual environment:
```
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Initialize the database and create test data:
```
python create_db.py
```

5. Run the application:
```
python app.py
```

6. Access the application at: http://127.0.0.1:5000

## Demo Accounts

The application comes with pre-seeded demo accounts for testing:

### Customer Account
- **Username**: customer
- **Password**: password123

### Restaurant Owner Account
- **Username**: owner
- **Password**: password123

## Usage Guide

### For Customers
1. Log in using the customer credentials
2. Browse restaurants or search for specific cuisines
3. View restaurant menus and add items to your cart
4. Place an order and track its status
5. Leave reviews for restaurants and menu items

### For Restaurant Owners
1. Log in using the owner credentials
2. Manage your restaurants and menu items
3. Process incoming orders by updating their status
4. View reports on sales and popular menu items

## Design Principles

The application follows several key design principles:

- **PEP 8 Compliance**: Following Python coding standards
- **SOLID Principles**: Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion
- **Layered Architecture**: Separation of concerns between data access, business logic, and presentation
- **Responsive Design**: Mobile-friendly interface using Bootstrap

## Testing

Run the unit tests using the following command:
```
python -m unittest discover tests
```

## Assumptions

- Address management, delivery management, and payment functionality are out of scope
- All prices are in Indian Rupees (₹)
- All locations are in Delhi, India
- Order tracking is simplified to status updates

## License

[MIT License](LICENSE)

## Author

Your Name