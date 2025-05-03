import redis
import mysql.connector
import ast  # to safely evaluate stringified dicts from Redis
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def flush_chat_to_mysql(chat_id):
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
        msg = ast.literal_eval(msg_str)  # safely convert string to dict
        cursor.execute("""
            INSERT INTO messages (chat_id, sender_id, sender_name, message_text, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            chat_id,
            int(msg["sender_id"]),
            msg["sender"],
            msg["text"],
            msg["timestamp"]
        ))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Flushed {len(messages)} messages from chat:{chat_id} to MySQL.")
    r.delete(messages_key)  # Cleanup Redis after flush