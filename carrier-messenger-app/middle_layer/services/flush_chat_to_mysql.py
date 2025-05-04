import redis
import mysql.connector
import ast

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def flush_chat_to_mysql(chat_id):
    print(f"📥 Flushing chat: {chat_id} from Redis to MySQL...")

    messages_key = f"chat:{chat_id}:messages"
    messages = r.lrange(messages_key, 0, -1)

    if not messages:
        print(f"⚠️ No messages found for chat {chat_id}")
        return

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="medic26861311()",
        database="carrier_messenger"
    )
    cursor = conn.cursor()

    for msg_str in messages:
        msg = ast.literal_eval(msg_str)  # Convert string to dict
        sender_id = int(msg["sender_id"])
        sender_name = msg["sender"]
        text = msg["text"]
        timestamp = msg["timestamp"]

        # Insert into messages table
        cursor.execute("""
            INSERT INTO messages (chat_id, sender_id, sender_name, message_text, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (chat_id, sender_id, sender_name, text, timestamp))

        # Insert into user_chats table
        cursor.execute("""
            INSERT IGNORE INTO user_chats (user_id, chat_id)
            VALUES (%s, %s)
        """, (sender_id, chat_id))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Flushed {len(messages)} messages from {chat_id} to MySQL.")
    r.delete(messages_key)