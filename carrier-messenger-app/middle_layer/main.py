from flask import Flask, request, jsonify
import redis
from flask_cors import CORS
from api.user_routes import user_bp

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers="*")

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

app.register_blueprint(user_bp)

# Redis Message Routes (unchanged)
@app.route('/messages/<chat_id>', methods=['GET'])
def get_messages(chat_id):
    messages = redis_client.lrange(f'chat:{chat_id}', 0, -1)
    return jsonify(messages)

@app.route('/messages', methods=['POST'])
def store_message():
    print("Received Request:", request.method, request.path)
    print("Headers:", request.headers)
    print("Raw Data:", request.data)
    print("JSON Data:", request.json)

    data = request.json
    if not data or 'chat_id' not in data or 'message' not in data:
        return jsonify({"error": "Invalid request"}), 400

    chat_id = data['chat_id']
    message = data['message']
    redis_client.rpush(f'chat:{chat_id}', message)
    return jsonify({"status": "Message stored"}), 201

@app.route('/messages/<chat_id>', methods=['DELETE'])
def delete_messages(chat_id):
    redis_client.delete(f'chat:{chat_id}')
    return jsonify({"status": "Chat deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)