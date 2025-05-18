import uuid
from app import db, redis_client
from app.models import User
from app.config import Config
from werkzeug.exceptions import Conflict, NotFound, Unauthorized
import redis

# Registers a new user after checking for conflicts and hashing the password
def register_user(username, email, password):
    if User.query.filter_by(username=username).first():
        raise Conflict("Username already exists")
    if User.query.filter_by(email=email).first():
        raise Conflict("Email already exists")

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        raise

# Authenticates user and returns a Redis-stored token if successful
def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        raise Unauthorized("Invalid username or password")

    token = uuid.uuid4().hex

    if not redis_client:
        print("ERROR: Redis client not initialized!")
        raise ConnectionError("Authentication service temporarily unavailable.")

    try:
        token_key = f"token:{token}"
        expiration_seconds = int(Config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
        redis_client.set(token_key, str(user.user_id), ex=expiration_seconds)
    except redis.exceptions.ConnectionError as e:
        print(f"ERROR: Could not connect to Redis during login: {e}")
        raise ConnectionError("Authentication service temporarily unavailable.")
    except Exception as e:
        print(f"ERROR: Unexpected error during Redis operation: {e}")
        raise

    return token

# Verifies the token against Redis and returns the associated user ID
def verify_token(token):
    if not redis_client:
        print("ERROR: Redis client not initialized!")
        return None

    try:
        user_id_str = redis_client.get(f"token:{token}")
        if user_id_str:
            return int(user_id_str)
        return None
    except redis.exceptions.ConnectionError as e:
        print(f"ERROR: Could not connect to Redis during token verification: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error during Redis token verification: {e}")
        return None
