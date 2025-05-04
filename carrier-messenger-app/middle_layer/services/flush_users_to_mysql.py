import redis
import mysql.connector

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def flush_user_to_mysql(user_id):
    user_key = f"user:temp:{user_id}"
    user_data = r.hgetall(user_key)

    if not user_data:
        print(f"⚠️ No user temp data found in Redis for user_id: {user_id}")
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="medic26861311()",
            database="carrier_messenger"
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash)
            VALUES (%s, %s, %s, %s)
        """, (
            int(user_id),
            user_data.get("username"),
            user_data.get("email"),
            user_data.get("password_hash")
        ))
        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Flushed user {user_data['username']} to MySQL.")
        r.delete(user_key)
    except Exception as e:
        print(f"❌ Error flushing user {user_id}: {e}")