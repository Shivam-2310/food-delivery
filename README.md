# JustEat - Food Ordering Application

A Flask-based food ordering application with a streamlined setup process.

## Features
- Customer and restaurant owner dashboards
- User authentication and role-based access
- Restaurant and menu management
- Order processing and tracking
- Feedback and rating system

## Tech Stack
- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF

## Project Structure
```
food-ordering-exit-test/
├── app/
│   ├── controllers/         # Route handlers
│   ├── forms/              # Form definitions
│   ├── models/             # Database models
│   ├── static/             # CSS, JS, images
│   ├── templates/          # HTML templates
│   ├── utils/              # Utility functions
│   └── __init__.py         # Application factory
├── instance/               # Database file (auto-created)
├── tests/                  # Unit tests
├── app.py                  # Application entry point
├── create_db.py            # Database initialization
├── seed_users.py           # User seeding script
└── requirements.txt        # Dependencies
```

## Prerequisites
- Python 3.11 or newer
- pip (bundled with Python)

## Setup Instructions

### 1) Clone/Copy the Project
```bash
# If using Git
git clone <your-repo-url>
cd food-ordering-exit-test

# Or copy the project folder to your desired location
```

### 2) Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3) Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Initialize Database
```bash
python create_db.py
```

### 5) Seed Demo Users
```bash
python seed_users.py
```

### 6) Run the Application
```bash
python app.py
```

### 7) Access the Application
Open your browser and navigate to: `http://127.0.0.1:5000`

## Demo Login Credentials

### Customers
- **Username**: `customer1` | **Password**: `password123` (Rahul Sharma)
- **Username**: `customer2` | **Password**: `password123` (Anita Verma)

### Restaurant Owners
- **Username**: `owner1` | **Password**: `password123` (Priya Patel)
- **Username**: `owner2` | **Password**: `password123` (Arjun Mehta)

## Quick Start Commands
```bash
# Complete setup in one go
python -m venv venv
venv\Scripts\activate                    # Windows
# source venv/bin/activate              # macOS/Linux
pip install -r requirements.txt
python create_db.py
python seed_users.py
python app.py
```

## Testing
Run the test suite:
```bash
python -m unittest discover tests
```

## File Locations
- **Database**: `instance/justeat.db` (created automatically)
- **Logs**: `justeat.log` (in project root)
- **Uploads**: `app/static/uploads/` (created automatically)

## Troubleshooting

### Windows PowerShell Script Execution Error
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Port Already in Use
```bash
# Stop the current process or use a different port
python app.py --port 5050
```

### Database Issues
```bash
# Delete database and recreate
rm instance/justeat.db          # macOS/Linux
del instance\justeat.db         # Windows
python create_db.py
python seed_users.py
```

### Virtual Environment Issues
```bash
# Deactivate and recreate
deactivate
rm -rf venv                     # macOS/Linux
rmdir /s venv                   # Windows
python -m venv venv
# Reactivate and reinstall
```

## Development Notes
- The application uses SQLite for simplicity
- No environment variables required for basic setup
- All demo data is created by `seed_users.py`
- Database tables are created by `create_db.py`
- Application entry point is `app.py`

## License
MIT