from flask import Blueprint, request, jsonify
import hashlib
import redis
from flask_cors import cross_origin

from services.redis_service import r
from services.retrieve_chats_for_user import hydrate_user_chats
from services.redis_service import store_user

user_bp = Blueprint('user', __name__)

########## Signup Router ##########
@user_bp.route('/signup', methods=['POST', 'OPTIONS'])
@cross_origin()
def signup():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return response, 200

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if not username or not email or not password or not confirm_password:
        return jsonify({"message": "Missing required fields"}), 400

    if password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    user_id = store_user(username, email, password)

    return jsonify({
        "message": "Signup successful",
        "user_id": user_id
    }), 201


########## Login Router ##########

@user_bp.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin()
def login():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    for key in r.scan_iter("user:*"):
        user = r.hgetall(key)
        if user.get("username") == username and user.get("password_hash") == password_hash:
            user_id = user.get("id")
            hydrate_user_chats(user_id)
            print(f"Matched user: {user['username']}, ID: {user['id']}")
            return jsonify({
                "message": "Login successful",
                "user_id": user_id,
                "username": username,
            }), 200

    return jsonify({"message": "Invalid credentials"}), 401

###### User profile router, for profile mini ########

@user_bp.route('/profile/<user_id>', methods=['GET'])
@cross_origin()
def get_user_profile(user_id):
    user_data = r.hgetall(f"user:{user_id}")
    if not user_data:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": user_data["id"],
        "username": user_data["username"],
        "email": user_data["email"],
        # "profilePhoto": user_data.get("profilePhoto", "")  # optional
    }), 200

####### user contacts router for sidebar ########

@user_bp.route('/contacts/<user_id>', methods=['GET'])
@cross_origin()
def get_user_contacts(user_id):
    # Fetch all message_token keys
    all_keys = r.keys('message_token:*')
    contacts = []

    for key in all_keys:
        chat_data = r.hgetall(key)
        if not chat_data:
            continue

        participants_raw = chat_data.get('participants')
        if not participants_raw:
            continue

        participant_ids = participants_raw.split(',')

        if user_id not in participant_ids:
            continue  # Skip chats the user is not part of

        # Remove self
        other_participants = [pid for pid in participant_ids if pid != user_id]

        enriched = []
        for pid in other_participants:
            user_info = r.hgetall(f"user:{pid}")
            if user_info:
                enriched.append({
                    "id": pid,
                    "username": user_info.get("username", "Unknown"),
                    # "profilePhoto": user_info.get("profilePhoto")
                })

        contacts.append({
            "chat_id": chat_data.get("chat_id"),
            "participants": enriched
        })

    return jsonify({"contacts": contacts})

########## Ping Router ##########

@user_bp.route('/ping', methods=['GET', 'OPTIONS'])
@cross_origin()
def ping():
    if request.method == 'OPTIONS':
        print("📡 Hit endpoint")
        return jsonify({'status': 'ok'}), 200

    print("📡 Ping received from frontend")
    return jsonify({"message": "Pong from Flask!"}), 200