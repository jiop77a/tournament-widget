from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # For cross-origin requests
from datetime import datetime

# Initialize the Flask application and the database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///instance/tournament.db"  # SQLite database
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable modification tracking

# Initialize SQLAlchemy and CORS
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for all routes


# Basic route to test the setup
@app.route("/")
def home():
    return "Tournament Widget API is running!"


if __name__ == "__main__":
    app.run(debug=True)
