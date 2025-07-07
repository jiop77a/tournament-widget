import os

from database import db
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS  # For cross-origin requests
from flask_migrate import Migrate

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# Initialize the Flask application and the database
app = Flask(__name__)

# Ensure instance directory exists
os.makedirs(app.instance_path, exist_ok=True)

# Use absolute path for SQLite database
db_path = os.path.join(app.instance_path, "tournament.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable modification tracking

# Initialize SQLAlchemy and CORS
db.init_app(app)
CORS(app)  # Enable CORS for all routes

# Import models after db initialization to avoid circular imports
import models

# Initialize Flask-Migrate after the models are loaded
migrate = Migrate(app, db)

# Import the Blueprint for tournament-related routes
from tournament_routes import tournament_bp

# Register the Blueprint with the Flask app
app.register_blueprint(tournament_bp, url_prefix="/api")


# Basic route to test the setup
@app.route("/")
def home():
    return "Tournament Widget API is running!"
