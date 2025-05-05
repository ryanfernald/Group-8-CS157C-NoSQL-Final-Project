# File: your_chat_project/app/api/routes_auth.py

from flask import Blueprint, request, jsonify
from app.services import auth_service # Import the service functions
from werkzeug.exceptions import BadRequest, Conflict, NotFound, Unauthorized, InternalServerError

# Create a Blueprint for authentication routes
# url_prefix='/auth' means all routes in this file will start with /auth
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint.
    Expects JSON: {"username": "...", "email": "...", "password": "..."}
    """
    data = request.get_json()

    # Basic input validation
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        # Use Werkzeug's BadRequest exception which Flask handles as 400
        raise BadRequest("Missing username, email, or password in request body")
    if not data['username'] or not data['email'] or not data['password']:
            raise BadRequest("Username, email, and password cannot be empty")

    username = data['username']
    email = data['email']
    password = data['password']

    try:
        # Call the registration service function
        new_user = auth_service.register_user(username, email, password)
        # Return success response with created user details (excluding password)
        return jsonify(message="User registered successfully", user=new_user.to_dict()), 201 # 201 Created
    except Conflict as e:
        # User or email already exists (409 Conflict)
        return jsonify(error=str(e)), 409
    except Exception as e:
        # Handle other unexpected errors (log them!)
        print(f"ERROR during registration: {e}") # Replace with proper logging
        # Raise InternalServerError which Flask handles as 500
        raise InternalServerError("An unexpected error occurred during registration.")


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    Expects JSON: {"username": "...", "password": "..."}
    """
    data = request.get_json()

    # Basic input validation
    if not data or not all(k in data for k in ('username', 'password')):
        raise BadRequest("Missing username or password in request body")
    if not data['username'] or not data['password']:
            raise BadRequest("Username and password cannot be empty")

    username = data['username']
    password = data['password']

    try:
        # Call the login service function
        token = auth_service.login_user(username, password)
        # Return success response with the token
        return jsonify(message="Login successful", token=token), 200 # 200 OK
    except (NotFound, Unauthorized) as e:
        # User not found or invalid password (401 Unauthorized)
        # We return 401 for both to avoid revealing which one was wrong (security)
        return jsonify(error="Invalid username or password"), 401
    except ConnectionError as e:
            # Handle cases where Redis might be down during login
            print(f"ERROR during login (Redis connection?): {e}") # Replace with proper logging
            return jsonify(error="Login service temporarily unavailable"), 503 # 503 Service Unavailable
    except Exception as e:
        # Handle other unexpected errors (log them!)
        print(f"ERROR during login: {e}") # Replace with proper logging
        raise InternalServerError("An unexpected error occurred during login.")

# Add a simple route to test token verification (optional)
@auth_bp.route('/verify', methods=['GET'])
def verify():
    """ Test endpoint to verify a token from Authorization header """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify(error="Missing or invalid Authorization header"), 401

    token = auth_header.split(' ')[1]
    user_id = auth_service.verify_token(token)

    if user_id:
        return jsonify(message="Token is valid", user_id=user_id), 200
    else:
        return jsonify(error="Invalid or expired token"), 401

