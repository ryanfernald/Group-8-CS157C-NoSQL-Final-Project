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
def create_chat():
    data = request.get_json()
    current_user_id = data.get('currentUserId')
    current_username = data.get('currentUsername')
    targets = data.get('targets', [])

    if not current_user_id or not current_username:
        return jsonify({"message": "Missing current user info"}), 400

    if not targets or not isinstance(targets, list):
        return jsonify({"message": "Invalid targets"}), 400

    # Get all user info and validate users exist
    participant_ids = [current_user_id]
    participant_usernames = [current_username]

    for identifier in targets:
        user = None

        # Try to find by username or email
        for key in r.scan_iter("user:*"):
            user_data = r.hgetall(key)
            if user_data.get("username") == identifier or user_data.get("email") == identifier:
                user = user_data
                break

        if not user:
            return jsonify({"message": f"User '{identifier}' not found"}), 404

        if user["username"] == current_username or user["email"] == current_username:
            return jsonify({"message": "Can't create a chat with yourself"}), 400

        participant_ids.append(user["id"])
        participant_usernames.append(user["username"])

    # Check for existing 1:1 chat with exact same participants
    for key in r.scan_iter("message_token:*"):
        token_data = r.hgetall(key)
        existing_participants = token_data.get("participants", "").split(',')
        if set(existing_participants) == set(participant_ids):
            return jsonify({"message": f"Chat already exists with {', '.join(participant_usernames[1:])}"}), 409

    # Create new chat
    unique_suffix = str(uuid.uuid4().hex[:4])
    chat_id = f"chat_{'_'.join(participant_usernames)}_{unique_suffix}"

    r.hset(f"message_token:{chat_id}", mapping={
        "chat_id": chat_id,
        "participants": ','.join(participant_ids),
        "created_at": datetime.utcnow().isoformat()
    })

    return jsonify({
        "message": "Chat created",
        "chat_id": chat_id,
        "created_with": participant_usernames[1:]
    }), 201


########### Delete Message Router ##########

@message_bp.route('/delete-participant', methods=['POST'])
@cross_origin()
def delete_participant():
    data = request.get_json()
    user_id = data.get('user_id')
    chat_id = data.get('chat_id')

    if not user_id or not chat_id:
        return jsonify({"message": "Missing user_id or chat_id"}), 400

    token_key = f"message_token:{chat_id}"
    if not r.exists(token_key):
        return jsonify({"message": "Chat does not exist"}), 404

    participants_raw = r.hget(token_key, "participants")
    if not participants_raw:
        return jsonify({"message": "Participants not found"}), 404

    participants = participants_raw.split(',')
    if user_id not in participants:
        return jsonify({"message": "User is not in this chat"}), 400

    participants.remove(user_id)

    if participants:
        r.hset(token_key, "participants", ",".join(participants))
    else:
        r.delete(token_key)  # Remove entire chat if no one is left

    return jsonify({"message": "User removed from chat"}), 200