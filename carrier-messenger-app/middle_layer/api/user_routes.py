from flask import Blueprint, request, jsonify
from services.mysql_service import create_user
from services.redis_service import store_user_temp, store_user_session_token
import hashlib

user_bp = Blueprint('user', __name__)

@user_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        # This handles the CORS preflight
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200

    # Handle actual signup request
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Store temporary user data in Redis
    temp_id = store_user_temp(username, email, password_hash)

    # Insert into MySQL
    user_id = create_user(username, email, password_hash)

    # Generate a session token and return it
    token = store_user_session_token(user_id, username)

    response = jsonify({
        "message": "Signup successful",
        "token": token,
        "user_id": user_id
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 201