# JustEat - Food Ordering Application

JustEat is a Flask-based food ordering application. The repository is streamlined with a single, clear seeding flow for development.

## Highlights
- `create_db.py` creates database tables only (no data insertion).
- `flask seed-data` inserts exactly two customers and two owners with Indian names and phone numbers. No restaurants or menu items are created by default.

## Tech Stack
- Backend: Flask
- Frontend: HTML, CSS, JavaScript (Bootstrap)
- Database: SQLite
- ORM: SQLAlchemy
- Authentication: Flask-Login
- Forms: Flask-WTF

## Project Structure
```
food-ordering-exit-test/
├── app/
│   ├── controllers/
│   ├── forms/
│   ├── models/
│   ├── static/
│   ├── templates/
│   ├── utils/
│   └── __init__.py
├── instance/                # Created automatically; holds justeat.db
├── tests/
├── app.py                   # Flask app + CLI (init-db, seed-data)
├── create_db.py             # Tables-only initialization script
└── requirements.txt
```

## Prerequisites
- Python 3.11 or newer
- pip (bundled with Python)

## Setup Instructions

### 1) Clone the Repository
```
git clone <your-repo-url>
cd food-ordering-exit-test
```

### 2) Create and Activate a Virtual Environment
- Windows (PowerShell):
```
python -m venv venv
./venv/Scripts/Activate.ps1
```
- macOS/Linux:
```
python3 -m venv venv
source venv/bin/activate
```

### 3) Install Dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Environment Configuration
Set the following environment variables in your shell session.

- Windows (PowerShell):
```
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
$env:SECRET_KEY="dev_key_only_for_development"
```
- macOS/Linux (bash/zsh):
```
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY=dev_key_only_for_development
```

### 5) Initialize the Database (choose ONE path)
- Simple (tables only):
```
python create_db.py
```
- Using migrations (if you have a working Alembic setup):
```
flask db upgrade
```

### 6) Seed Development Data
Inserts two customers and two owners (no restaurants or menu items):
```
flask seed-data
```

### 7) Run the Application
```
python app.py
```
Navigate to: http://127.0.0.1:5000

## Demo Accounts
- Customers
  - customer1 / password123
  - customer2 / password123
- Owners
  - owner1 / password123
  - owner2 / password123

## Configuration Notes
- SQLite database is created at `instance/justeat.db`.
- Logs are written to `justeat.log` in the project root.
- Uploads directory is `app/static/uploads` (created automatically).

## Testing
```
python -m unittest discover tests
```

## Troubleshooting
- Windows script activation error when running `Activate.ps1`:
  - Open PowerShell as current user and run:
  ```
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
  Then re-run `./venv/Scripts/Activate.ps1`.
- Port already in use:
  - Stop the other process or set a different port:
  ```
  set FLASK_RUN_PORT=5050   # Windows
  export FLASK_RUN_PORT=5050 # macOS/Linux
  python app.py
  ```

## License
MIT