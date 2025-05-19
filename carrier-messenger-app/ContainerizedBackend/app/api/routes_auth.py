from flask import Blueprint, request, jsonify
from app.services import auth_service
from werkzeug.exceptions import BadRequest, Conflict, NotFound, Unauthorized, InternalServerError

# Defines authentication-related routes under the '/auth' URL prefix
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# Handles user registration requests
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        raise BadRequest("Missing username, email, or password in request body")
    if not data['username'] or not data['email'] or not data['password']:
        raise BadRequest("Username, email, and password cannot be empty")

    username = data['username']
    email = data['email']
    password = data['password']

    try:
        new_user = auth_service.register_user(username, email, password)
        return jsonify(message="User registered successfully", user=new_user.to_dict()), 201
    except Conflict as e:
        return jsonify(error=str(e)), 409
    except Exception as e:
        print(f"ERROR during registration: {e}")
        raise InternalServerError("An unexpected error occurred during registration.")

# Handles user login requests and returns a token if successful
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'password')):
        raise BadRequest("Missing username or password in request body")
    if not data['username'] or not data['password']:
        raise BadRequest("Username and password cannot be empty")

    username = data['username']
    password = data['password']

    try:
        token = auth_service.login_user(username, password)
        return jsonify(message="Login successful", token=token), 200
    except (NotFound, Unauthorized) as e:
        return jsonify(error="Invalid username or password"), 401
    except ConnectionError as e:
        print(f"ERROR during login (Redis connection?): {e}")
        return jsonify(error="Login service temporarily unavailable"), 503
    except Exception as e:
        print(f"ERROR during login: {e}")
        raise InternalServerError("An unexpected error occurred during login.")

# Verifies a JWT token passed in the Authorization header
@auth_bp.route('/verify', methods=['GET'])
def verify():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify(error="Missing or invalid Authorization header"), 401

    token = auth_header.split(' ')[1]
    user_id = auth_service.verify_token(token)

    if user_id:
        return jsonify(message="Token is valid", user_id=user_id), 200
    else:
        return jsonify(error="Invalid or expired token"), 401
