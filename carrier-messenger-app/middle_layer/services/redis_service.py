# Handles Redis get/set/add

import redis
from config import Config

r = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

def cache_session(token, username):
    r.setex(token, 3600, username)  # 1 hour session expiration

def get_session_user(token):
    return r.get(token)