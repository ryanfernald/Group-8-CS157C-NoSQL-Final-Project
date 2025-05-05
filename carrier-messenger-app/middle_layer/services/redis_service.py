import redis
import hashlib
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def generate_unique_user_id():
    """Generate a unique 6-digit user ID that doesn't already exist in Redis."""
    while True:
        user_id = str(random.randint(100000, 999999))
        if not r.exists(f"user:{user_id}"):
            return user_id

def store_user(username, email, password):
    """Store a new user in Redis with no expiration."""
    user_id = generate_unique_user_id()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user_data = {
        "id": user_id,
        "username": username,
        "email": email,
        "password_hash": password_hash
    }
    r.hset(f"user:{user_id}", mapping=user_data)
    print(f"🟢 Stored user in Redis with key user:{user_id}")
    return user_id

def get_all_users():
    """Optional helper to retrieve all users (for testing/debug)."""
    users = []
    for key in r.scan_iter("user:*"):
        users.append(r.hgetall(key))
    return users