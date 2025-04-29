from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
from api.user_routes import user_bp

app = Flask(__name__)

# CORRECT CORS SETUP
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=False  # NO cookies needed yet
)

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

app.register_blueprint(user_bp)

# Simple root endpoint for testing
@app.route('/')
def index():
    return jsonify({"message": "Hello from Flask backend!"})

# Redis message routes (you can keep these)
@app.route('/messages/<chat_id>', methods=['GET', 'OPTIONS'])
def get_messages(chat_id):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    messages = redis_client.lrange(f'chat:{chat_id}', 0, -1)
    return jsonify(messages)

@app.route('/messages', methods=['POST', 'OPTIONS'])
def store_message():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    data = request.json
    chat_id = data['chat_id']
    message = data['message']
    redis_client.rpush(f'chat:{chat_id}', message)
    return jsonify({"status": "Message stored"}), 201

if __name__ == '__main__':
    app.run(debug=True)