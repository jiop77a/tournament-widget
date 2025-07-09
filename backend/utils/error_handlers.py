"""
Error handling utilities for consistent API responses
"""

from functools import wraps

from flask import jsonify
from werkzeug.exceptions import HTTPException


def handle_api_errors(f):
    """
    Decorator to provide consistent error handling for API routes

    Catches common exceptions and returns standardized JSON error responses:
    - ValueError -> 400 Bad Request
    - HTTPException (404, etc.) -> Original status code
    - Other exceptions -> 500 Internal Server Error

    Usage:
        @handle_api_errors
        def my_route():
            # Your route logic here
            pass
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except HTTPException as e:
            # Handle Flask abort() calls (like 404, 500, etc.)
            return jsonify({"error": e.description or str(e)}), e.code
        except Exception as e:
            # Log unexpected errors for debugging
            print(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({"error": "Internal server error"}), 500

    return decorated_function
