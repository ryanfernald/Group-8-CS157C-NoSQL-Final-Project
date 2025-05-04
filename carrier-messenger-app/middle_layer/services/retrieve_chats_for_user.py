import redis
import mysql.connector

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def hydrate_user_chats(user_id):
    print(f"🟢 Hydrating chats for user_id: {user_id}")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="medic26861311()",
        database="carrier_messenger"
    )
    cursor = conn.cursor(dictionary=True)

    # Find chats from user_chats
    cursor.execute("""
        SELECT chat_id FROM user_chats WHERE user_id = %s
    """, (user_id,))
    chats = cursor.fetchall()

    for row in chats:
        chat_id = row["chat_id"]
        message_key = f"chat:{chat_id}:messages"
        chat_token_key = f"message_token:{chat_id}"

        # Load chat metadata
        cursor.execute("""
            SELECT DISTINCT sender_id FROM messages WHERE chat_id = %s
        """, (chat_id,))
        participants = [str(row["sender_id"]) for row in cursor.fetchall()]
        r.hset(chat_token_key, mapping={
            "chat_id": chat_id,
            "participants": ','.join(participants),
        })
        r.expire(chat_token_key, 1200)  # Optional: 20 minutes

        # Load recent 20 messages
        cursor.execute("""
            SELECT sender_id, sender_name, message_text, timestamp
            FROM messages
            WHERE chat_id = %s
            ORDER BY timestamp DESC
            LIMIT 20
        """, (chat_id,))
        messages = cursor.fetchall()

        for msg in reversed(messages):  # reverse to restore chronological order
            r.rpush(message_key, str({
                "sender_id": msg["sender_id"],
                "sender": msg["sender_name"],
                "text": msg["message_text"],
                "timestamp": msg["timestamp"]
            }))

        print(f"✅ Loaded chat:{chat_id} into Redis.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    hydrate_user_chats(101)