from flask import Flask, jsonify
# from flask_cors import CORS
import threading
from api.user_routes import user_bp

app = Flask(__name__)

from flask_cors import CORS

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

CORS(user_bp, resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}})

@app.route('/')
def index():
    return jsonify({"message": "Carrier Messenger API is running."})


def start_monitor_chats():
    from services.monitor_chats import listen_for_chat_expiry
    listen_for_chat_expiry()

def start_monitor_users():
    from services.monitor_user import monitor_user_tokens
    monitor_user_tokens()

app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    # Start background services
    threading.Thread(target=start_monitor_chats, daemon=True).start()
    threading.Thread(target=start_monitor_users, daemon=True).start()

    app.run(debug=True, port=5000)