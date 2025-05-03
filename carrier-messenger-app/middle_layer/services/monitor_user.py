import redis
import mysql.connector
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def flush_user_by_id(user_id):
    user_key = f"user:temp:{user_id}"
    user_data = r.hgetall(user_key)

    if not user_data:
        print(f"⚠️ No user data found for user_id {user_id}")
        return

    # Insert into MySQL
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="medic26861311()",
            database="carrier_messenger"
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """, (user_data['username'], user_data['email'], user_data['password_hash']))
        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Flushed user {user_data['username']} (ID {user_id}) from Redis to MySQL.")
    except Exception as e:
        print(f"❌ Error flushing user {user_id}: {e}")

    # Clean up Redis keys
    r.delete(user_key)

def listen_for_expired_tokens():
    pubsub = r.pubsub()
    pubsub.psubscribe('__keyevent@0__:expired')

    print("🔄 Listening for Redis key expirations...")
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            expired_key = message['data']
            if expired_key.startswith("user_token:"):
                token = expired_key.replace("user_token:", "")
                user_id = token.replace("tk", "")  # Based on token naming convention tk<user_id>
                flush_user_by_id(user_id)

def manual_logout(user_id):
    """Call this when a user clicks 'logout'."""
    token_key = f"user_token:tk{user_id}"
    r.delete(token_key)
    flush_user_by_id(user_id)

# Entry point
if __name__ == "__main__":
    try:
        listen_for_expired_tokens()
    except KeyboardInterrupt:
        print("🛑 Stopped monitoring.")