from app import app, db

# Push the application context
with app.app_context():
    db.create_all()  # Create all tables based on models
    print("Database created successfully!")
