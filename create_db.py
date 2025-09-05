"""Database initialization script (tables only)."""

from app import create_app, db

# Create app context and create tables only.
app = create_app()
with app.app_context():
    db.create_all()
    print("DATABASE TABLES CREATED SUCCESSFULLY!")
