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

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/justeat.git
cd justeat
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```
pip install -r requirements.txt
```

4. Initialize and seed the database:
```
flask init-db
flask seed-data
```

5. Run the application:
```
flask run
```

6. Access the application at: http://127.0.0.1:5000

## Demo Accounts

The application comes pre-seeded with two demo accounts:

### Customer Account
- **Username**: customer
- **Password**: password123

### Restaurant Owner Account
- **Username**: owner
- **Password**: password123

## Project Structure

- **app/** - Main application package
  - **controllers/** - Route controllers
  - **models/** - Database models
  - **forms/** - Form classes using Flask-WTF
  - **services/** - Business logic services
  - **static/** - Static files (CSS, JS, images)
  - **templates/** - Jinja2 templates
  - **utils/** - Utility functions
- **tests/** - Unit and integration tests

## Testing

Run tests using the unittest module:
```
python -m unittest discover tests
```

## Features and Design Decisions

### Architecture
- Layered architecture with separation of concerns
- MVC pattern with Flask blueprints for modular design
- RESTful route structure

### Security
- Password hashing with Werkzeug security
- Role-based access control
- CSRF protection with Flask-WTF

### User Experience
- Responsive design for mobile and desktop
- Flash messages for user feedback
- Form validation with clear error messages
- Intuitive navigation and workflow

## License

[MIT License](LICENSE)

## Acknowledgments

- This project was created as an assignment
- Images used in this project are from Unsplash
