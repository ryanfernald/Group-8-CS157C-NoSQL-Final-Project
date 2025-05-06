# Endpoints like /send, /fetch

from flask import Blueprint, request, jsonify
import hashlib
import redis
import json
from datetime import datetime
import uuid
from flask_cors import cross_origin

from services.redis_service import r

message_bp = Blueprint('messages', __name__)

############ Fetch Messages Router ##########

@message_bp.route('/<chat_id>', methods=['GET'])
@cross_origin()
def get_messages(chat_id):
    print(f"📩 Received GET for chat_id: {chat_id}")
    key = f"chat:{chat_id}:messages"
    messages_raw = r.lrange(key, 0, -1)

    if not messages_raw:
        print(f"⚠️ No messages found for key {key}")
        return jsonify({"messages": []}), 200

    messages = [eval(m) for m in messages_raw]  # Use json.loads() if JSON, eval() if string dicts
    return jsonify({"messages": messages}), 200


########### Send Message Router ##########

@message_bp.route('/<chat_id>', methods=['POST'])
@cross_origin()
def post_message(chat_id):
    data = request.get_json()
    sender_id = data.get('sender_id')
    sender = data.get('sender')
    text = data.get('text')

    if not sender_id or not sender or not text:
        return jsonify({"error": "Missing fields"}), 400

    message = {
        "sender_id": sender_id,
        "sender": sender,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }

    r.rpush(f'chat:{chat_id}:messages', str(message))
    return jsonify({"status": "Message stored"}), 201

########### Create New Chat Router ##########

@message_bp.route('/new-chat', methods=['POST'])
@cross_origin()
def create_new_chat():
    data = request.get_json()
    current_user_id = data.get('currentUserId')
    current_username = data.get('currentUsername')
    target_input = data.get('target')  # Can be username or email

    if not all([current_user_id, current_username, target_input]):
        return jsonify({"message": "Missing required fields"}), 400

    # Step 1: Find target user by username or email
    target_user_id = None
    target_username = None

    for key in r.scan_iter("user:*"):
        user_data = r.hgetall(key)
        if user_data.get('username') == target_input or user_data.get('email') == target_input:
            target_user_id = key.split(":")[1]
            target_username = user_data.get('username')
            break

    if not target_user_id:
        return jsonify({"message": "User not found"}), 404
    
    if target_user_id == current_user_id:
        return jsonify({"message": "Can't create a chat with yourself."}), 400

    # Step 2: Check if chat already exists between just these two users
    existing_chat = None
    for key in r.scan_iter("message_token:*"):
        chat_data = r.hgetall(key)
        participants = chat_data.get('participants', '')
        participant_list = participants.split(",")
        if set(participant_list) == {current_user_id, target_user_id}:
            existing_chat = key
            break

    if existing_chat:
        return jsonify({"message": f"Chat already exists with {target_username}"}), 400

    # Step 3: Create new chat
    chat_id = f"chat_{current_username.lower()}_{target_username.lower()}_{uuid.uuid4().hex[:4]}"
    r.hset(f"message_token:{chat_id}", mapping={
        "chat_id": chat_id,
        "participants": f"{current_user_id},{target_user_id}",
        "created_at": datetime.utcnow().isoformat()
    })

    return jsonify({
        "message": "Chat created",
        "chat_id": chat_id,
        "other_username": target_username
    }), 201