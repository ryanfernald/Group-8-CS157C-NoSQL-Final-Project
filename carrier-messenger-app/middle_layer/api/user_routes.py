# e.g., /register, /get_profile

from flask import Blueprint, request, jsonify
from services.mysql_service import fetch_user, create_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = fetch_user(username)
    
    if user and user['password'] == password:
        return jsonify({"message": "Login successful", "username": username}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@user_bp.route('/signup', methods=['POST'])
def signup():
    try:
        print("🔵 Signup route triggered")  # <-- added
        data = request.json
        print("🟡 Received signup data:", data)  # <-- added
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            print("🔴 Missing signup fields!")  # <-- added
            return jsonify({"message": "Missing required fields"}), 400

        user = fetch_user(username)
        if user:
            print("🔴 Username already exists!")  # <-- added
            return jsonify({"message": "Username already exists"}), 409

        create_user(username, email, password)
        print("🟢 User created successfully!")  # <-- added
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        print("🔥 Error in signup route:", e)  # <-- added
        return jsonify({"message": "Signup server error"}), 500
    
@user_bp.route('/test-insert', methods=['POST', 'OPTIONS'])  # <-- allow OPTIONS
def test_insert():
    if request.method == 'OPTIONS':
        # CORS preflight request
        return jsonify({"status": "OK"}), 200

    try:
        print("🔵 Test Insert Route triggered")

        dummy_username = "dummyuser"
        dummy_email = "dummy@example.com"
        dummy_password = "dummypass"

        from services.mysql_service import create_user
        create_user(dummy_username, dummy_email, dummy_password)

        print("🟢 Dummy user inserted into database!")
        return jsonify({"message": "Dummy user created successfully!"}), 201
    except Exception as e:
        print("❌ Error in test-insert route:", e)
        return jsonify({"message": "Failed to insert dummy user"}), 500