import redis
import json
import uuid

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def store_user_temp(username, email, password_hash):
    temp_id = f"user:{uuid.uuid4().hex}"
    r.hset(temp_id, mapping={
        "username": username,
        "email": email,
        "password_hash": password_hash
    })
    return temp_id

def store_user_session_token(user_id, username):
    token = uuid.uuid4().hex
    r.hset(f"user_token:{token}", mapping={
        "user_id": user_id,
        "username": username
    })
    r.expire(f"user_token:{token}", 1200)
    return token