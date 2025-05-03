import redis
import mysql.connector

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def flush_users_to_mysql():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="medic26861311()",
        database="carrier_messenger"
    )
    cursor = conn.cursor()

    for key in r.scan_iter("user:temp:*"):
        user = r.hgetall(key)
        username = user.get("username")
        email = user.get("email")
        password_hash = user.get("password_hash")

        if not username or not password_hash:
            continue

        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """, (username, email, password_hash))

        print(f"✔️ Flushed {username} to MySQL.")
        r.delete(key)  # Remove temp user from Redis

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    flush_users_to_mysql()