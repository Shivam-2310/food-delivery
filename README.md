# JustEat - Food Ordering Application

A Flask-based food ordering app. This repo now has a single, simplified seeding flow.

## What changed (simplified seeding)
- `create_db.py` only creates database tables. It does NOT insert any data.
- `flask seed-data` creates exactly 2 customers and 2 owners with Indian names and phone numbers. No restaurants or menu items are created by default.

## Tech Stack

- **Backend**: Flask
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Auth**: Flask-Login
- **Forms**: Flask-WTF

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
├── instance/
├── tests/
├── app.py                # Flask app + CLI (init-db, seed-data)
├── create_db.py          # Tables-only init script
└── requirements.txt
```

## Setup (Windows PowerShell)

1. Install Python 3.11+ and ensure it's on PATH.
2. Create and activate a virtual environment:
```
python -m venv venv
./venv/Scripts/Activate.ps1
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Set environment variables for this session:
```
$env:FLASK_APP="app.py"
$env:FLASK_ENV="development"
$env:SECRET_KEY="dev_key_only_for_development"
```
5. Create database tables (choose ONE):
```
# Option A (simple):
python create_db.py

# Option B (migrations, if you use them):
flask db upgrade
```
6. Seed demo users (2 customers, 2 owners; no restaurants):
```
flask seed-data
```
7. Run the app:
```
python app.py
```
Open http://127.0.0.1:5000

## Demo Accounts

- Customers:
  - customer1 / password123
  - customer2 / password123
- Owners:
  - owner1 / password123
  - owner2 / password123

## Notes
- DB file is stored at `instance/justeat.db`. It’s created automatically.
- Logs are written to `justeat.log`.
- Uploads are stored in `app/static/uploads`.

## Tests
```
python -m unittest discover tests
```