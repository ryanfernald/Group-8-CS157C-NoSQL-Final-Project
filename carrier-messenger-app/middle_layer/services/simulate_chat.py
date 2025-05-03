import csv
import redis
import uuid
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def create_user_token(user_id, username):
    token = f"tk{user_id}"
    r.hset(f"user_token:{token}", mapping={
        "user_id": user_id,
        "username": username
    })
    r.expire(f"user_token:{token}", 3600)  # Optional: 1 hour session
    return token

def create_chat(chat_id, participants):
    chat_key = f"message_token:{chat_id}"
    r.hset(chat_key, mapping={
        "chat_id": chat_id,
        "participants": ','.join(participants),
        "created_at": datetime.utcnow().isoformat()
    })

def insert_message(chat_id, sender_token, text):
    sender_info = r.hgetall(f"user_token:{sender_token}")
    if not sender_info:
        print(f"❌ Invalid or expired token {sender_token}")
        return

    message = {
        "sender_id": sender_info["user_id"],
        "sender": sender_info["username"],
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
    r.rpush(f"chat:{chat_id}:messages", str(message))  # Store as stringified dict

def simulate_chat_from_csv(csv_path):
    # Step 1: Create users
    romeo_token = create_user_token("101", "ROMEO")
    juliet_token = create_user_token("102", "JULIET")

    # Step 2: Create chat room
    chat_id = "chat_rj1"
    create_chat(chat_id, ["101", "102"])

    # Step 3: Read CSV and insert lines as messages
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            player = row['Player'].upper()
            line = row['PlayerLine']
            token = romeo_token if player == "ROMEO" else juliet_token
            insert_message(chat_id, token, line)

    print("✅ Romeo & Juliet chat simulated successfully.")

if __name__ == "__main__":
    simulate_chat_from_csv("romeo_juliet.csv")