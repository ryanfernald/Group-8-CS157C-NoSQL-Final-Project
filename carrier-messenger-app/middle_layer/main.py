from flask import Flask, jsonify
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def index():
    return jsonify({"message": "Carrier Messenger API is running."})

# === Background Services === #
def start_monitor_chats():
    from services.monitor_chats import listen_for_chat_expiry
    listen_for_chat_expiry()

def start_monitor_users():
    from services.monitor_user import monitor_user_tokens
    monitor_user_tokens()

# === Launch === #
if __name__ == "__main__":
    # Start Redis monitor threads
    threading.Thread(target=start_monitor_chats, daemon=True).start()
    threading.Thread(target=start_monitor_users, daemon=True).start()

    # Start Flask app
    app.run(debug=True, port=5000)