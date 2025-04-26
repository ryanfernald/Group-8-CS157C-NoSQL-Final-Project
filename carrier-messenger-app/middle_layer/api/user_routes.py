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
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    user = fetch_user(username)
    if user:
        return jsonify({"message": "Username already exists"}), 409

    create_user(username, email, password)
    return jsonify({"message": "User created successfully"}), 201