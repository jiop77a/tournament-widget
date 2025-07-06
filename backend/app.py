from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # For cross-origin requests
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application and the database
app = Flask(__name__)

# Ensure instance directory exists
os.makedirs(app.instance_path, exist_ok=True)

# Use absolute path for SQLite database
db_path = os.path.join(app.instance_path, "tournament.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable modification tracking

# Initialize SQLAlchemy and CORS
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for all routes

# Import models after db initialization to avoid circular imports
from models import InputQuestion, Prompt, Tournament, Match, PromptMetaData

# Initialize Flask-Migrate after the models are loaded
migrate = Migrate(app, db)


# Basic route to test the setup
@app.route("/")
def home():
    return "Tournament Widget API is running!"


if __name__ == "__main__":
    app.run(debug=True)
