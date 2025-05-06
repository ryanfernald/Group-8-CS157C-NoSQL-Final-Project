# Endpoints like /send, /fetch

from flask import Blueprint, request, jsonify
import hashlib
import redis
import json
from flask_cors import cross_origin

from services.redis_service import r

message_bp = Blueprint('messages', __name__)

########## Send Message Router ##########

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