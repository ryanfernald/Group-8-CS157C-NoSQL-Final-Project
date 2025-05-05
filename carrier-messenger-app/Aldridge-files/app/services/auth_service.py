# File: your_chat_project/app/services/auth_service.py

import uuid
from app import db, redis_client # Import db and redis_client
from app.models import User
from app.config import Config # Import Config to get expiration time
from werkzeug.exceptions import Conflict, NotFound, Unauthorized # Use standard exceptions
import redis
# Define custom exceptions if needed for more specific cases, but standard ones often suffice
# class UserExistsError(Conflict): pass
# class UserNotFoundError(NotFound): pass
# class InvalidPasswordError(Unauthorized): pass

def register_user(username, email, password):
    """
    Registers a new user.
    Checks for existing username/email. Hashes password. Saves to DB.
    Returns the new User object.
    Raises Conflict if username/email exists.
    """
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        raise Conflict("Username already exists") # 409 Conflict

    # Check if email already exists
    if User.query.filter_by(email=email).first():
        raise Conflict("Email already exists") # 409 Conflict

    # Create new user instance
    new_user = User(username=username, email=email)
    new_user.set_password(password) # Hash the password

    # Add to session and commit to database
    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback() # Rollback in case of error during commit
        # Log the exception e
        raise # Re-raise the exception for the API layer to handle as 500

def login_user(username, password):
    """
    Logs in an existing user.
    Verifies credentials. Generates and stores token in Redis.
    Returns the authentication token.
    Raises NotFound if user doesn't exist.
    Raises Unauthorized if password is incorrect.
    Raises ConnectionError if Redis is down.
    """
    # Find user by username
    user = User.query.filter_by(username=username).first()

    # Check if user exists and password is correct
    if user is None or not user.check_password(password):
        raise Unauthorized("Invalid username or password") # 401 Unauthorized

    # Generate a unique token
    token = uuid.uuid4().hex

    # Ensure redis_client is available
    if not redis_client:
            # Log this error
            print("ERROR: Redis client not initialized!") # Replace with proper logging
            raise ConnectionError("Authentication service temporarily unavailable.") # Or return 503

    # Store token in Redis with expiration
    try:
        token_key = f"token:{token}"
        expiration_seconds = int(Config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds())
        redis_client.set(token_key, str(user.user_id), ex=expiration_seconds)
    except redis.exceptions.ConnectionError as e:
            # Log this error
            print(f"ERROR: Could not connect to Redis during login: {e}") # Replace with proper logging
            raise ConnectionError("Authentication service temporarily unavailable.") # Or return 503
    except Exception as e:
            # Log unexpected errors during Redis operation
            print(f"ERROR: Unexpected error during Redis operation: {e}") # Replace with proper logging
            raise # Re-raise for API layer to handle as 500


    return token

def verify_token(token):
    """
    Verifies a token against Redis.
    Returns the user_id if valid, None otherwise.
    """
    if not redis_client:
        print("ERROR: Redis client not initialized!") # Replace with proper logging
        return None # Cannot verify without Redis

    try:
        user_id_str = redis_client.get(f"token:{token}")
        if user_id_str:
            # Optionally, refresh the token's TTL here if desired
            # redis_client.expire(f"token:{token}", int(Config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds()))
            return int(user_id_str)
        return None
    except redis.exceptions.ConnectionError as e:
        print(f"ERROR: Could not connect to Redis during token verification: {e}") # Replace with proper logging
        return None # Treat as invalid if Redis is down
    except Exception as e:
        print(f"ERROR: Unexpected error during Redis token verification: {e}") # Replace with proper logging
        return None


