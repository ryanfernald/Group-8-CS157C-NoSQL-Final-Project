import csv
import redis
import mysql.connector
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ---------------- MYSQL CONNECTION ---------------- #
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="medic26861311()",
        database="carrier_messenger"
    )

# ---------------- MYSQL USER & CHAT SETUP ---------------- #
def create_user(user_id, username, email, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (id, username, email, password_hash)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE username = VALUES(username)
    """, (user_id, username, email, password_hash))
    conn.commit()
    cursor.close()
    conn.close()

def link_user_to_chat(user_id, chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT IGNORE INTO user_chats (user_id, chat_id)
        VALUES (%s, %s)
    """, (user_id, chat_id))
    conn.commit()
    cursor.close()
    conn.close()

# ---------------- REDIS TOKEN & CHAT SETUP ---------------- #
def create_user_token(user_id, username):
    token = f"tk{user_id}"
    r.hset(f"user_token:{token}", mapping={
        "user_id": user_id,
        "username": username
    })
    r.expire(f"user_token:{token}", 3600)  # 1 hour
    return token

def create_chat(chat_id, participants):
    r.hset(f"message_token:{chat_id}", mapping={
        "chat_id": chat_id,
        "participants": ','.join(participants),
        "created_at": datetime.utcnow().isoformat()
    })
    r.expire(f"message_token:{chat_id}", 3600)

def insert_message(chat_id, sender_token, text):
    sender_info = r.hgetall(f"user_token:{sender_token}")
    if not sender_info:
        print(f"❌ Token {sender_token} is invalid or expired.")
        return

    message = {
        "sender_id": sender_info["user_id"],
        "sender": sender_info["username"],
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
    r.rpush(f"chat:{chat_id}:messages", str(message))

# ---------------- MAIN SIMULATION ---------------- #
def simulate_chat_from_csv(csv_path):
    # 1. Create users in MySQL
    create_user("101", "ROMEO", "romeo@email.com", "hash_romeo")
    create_user("102", "JULIET", "juliet@email.com", "hash_juliet")

    # 2. Token + Chat setup
    romeo_token = create_user_token("101", "ROMEO")
    juliet_token = create_user_token("102", "JULIET")
    chat_id = "chat_rj1"
    create_chat(chat_id, ["101", "102"])

    # 3. Link users to the chat (user_chats table)
    link_user_to_chat("101", chat_id)
    link_user_to_chat("102", chat_id)

    # 4. Insert messages into Redis
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            player = row['Player'].upper()
            line = row['PlayerLine']
            token = romeo_token if player == "ROMEO" else juliet_token
            insert_message(chat_id, token, line)

    print("✅ Simulated chat between ROMEO and JULIET completed.")

# Run it
if __name__ == "__main__":
    simulate_chat_from_csv("romeo_juliet.csv")