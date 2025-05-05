from flask import Blueprint, request, jsonify
from services.mysql_service import create_user
from services.redis_service import store_user_temp, store_user_session_token
import hashlib
from flask_cors import cross_origin

user_bp = Blueprint('user', __name__)

@user_bp.route('/signup', methods=['POST', 'OPTIONS'])
@cross_origin()
def signup():
    if request.method == 'OPTIONS':
        # This handles the CORS preflight
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://127.0.1:5173')
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

@user_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin()
def login():
    print("📥 Login endpoint hit") 
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200

    data = request.get_json()
    user_id = data.get('user_id')
    username = data.get('username')

    if not user_id or not username:
        return jsonify({"message": "Missing user_id or username"}), 400

    from services.redis_service import redis_client
    from services.retrieve_chats_for_user import hydrate_user_chats

    token = f"tk{user_id}"
    redis_client.hset(f"user_token:{token}", mapping={
        "user_id": user_id,
        "username": username
    })
    redis_client.expire(f"user_token:{token}", 1200)

    hydrate_user_chats(user_id)

    response = jsonify({
        "message": "Login successful",
        "token": token
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 200


@user_bp.route('/ping', methods=['GET', 'OPTIONS'])
@cross_origin()
def ping():
    if request.method == 'OPTIONS':
        print("📡 Hit endpoint")
        return jsonify({'status': 'ok'}), 200

    print("📡 Ping received from frontend")
    return jsonify({"message": "Pong from Flask!"}), 200