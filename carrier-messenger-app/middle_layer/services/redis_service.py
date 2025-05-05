import redis
import json
import uuid

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def store_user_temp(username, email, password_hash, expire_seconds=1200):
    temp_id = f"user_temp:{uuid.uuid4().hex[:8]}"
    user_data = {
        "username": username,
        "email": email,
        "password_hash": password_hash
    }

    r.hset(temp_id, mapping=user_data)
    r.expire(temp_id, expire_seconds)

    print(f"🟢 Stored temp user in Redis with key {temp_id}")
    return temp_id
def store_user_session_token(user_id, username):
    token = uuid.uuid4().hex
    r.hset(f"user_token:{token}", mapping={
        "user_id": user_id,
        "username": username
    })
    r.expire(f"user_token:{token}", 1200)
    return token