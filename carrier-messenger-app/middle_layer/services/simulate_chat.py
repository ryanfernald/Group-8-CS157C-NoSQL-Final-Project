import csv
import redis
from datetime import datetime
import hashlib

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ---------------- REDIS USER & CHAT SETUP ---------------- #
def create_user(user_id, username, email, raw_password):
    password_hash = hashlib.sha256(raw_password.encode()).hexdigest()
    r.hset(f"user:{user_id}", mapping={
        "id": user_id,
        "username": username,
        "email": email,
        "password_hash": password_hash
    })

def create_chat(chat_id, participants):
    r.hset(f"message_token:{chat_id}", mapping={
        "chat_id": chat_id,
        "participants": ','.join(participants),
        "created_at": datetime.utcnow().isoformat()
    })

def insert_message(chat_id, user_id, text):
    sender_info = r.hgetall(f"user:{user_id}")
    if not sender_info:
        print(f"❌ User {user_id} not found.")
        return

    message = {
        "sender_id": sender_info["id"],
        "sender": sender_info["username"],
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
    r.rpush(f"chat:{chat_id}:messages", str(message))

# ---------------- MAIN SIMULATION ---------------- #
def simulate_chat_from_csv(csv_path):
    # 1. Create users in Redis
    create_user("736345", "ROMEO", "romeo@email.com", "romeo123")
    create_user("356784", "JULIET", "juliet@email.com", "juliet123")

    # 2. Create chat
    chat_id = "chat_rj1"
    create_chat(chat_id, ["736345", "356784"])

    # 3. Insert messages into Redis
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            player = row['Player'].upper()
            line = row['PlayerLine']
            user_id = "736345" if player == "ROMEO" else "356784"
            insert_message(chat_id, user_id, line)

    print("✅ Simulated chat between ROMEO and JULIET completed.")

# Run it
if __name__ == "__main__":
    simulate_chat_from_csv("romeo_juliet.csv")