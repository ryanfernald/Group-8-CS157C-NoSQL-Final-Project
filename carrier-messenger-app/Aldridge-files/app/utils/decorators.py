# File: your_chat_project/app/utils/decorators.py

from functools import wraps
from flask import request, jsonify, current_app
from app.services import auth_service # Import the verification function
from app.models import User # Import User model to potentially attach user to request context

# --- Ensure this function definition is exactly correct ---
def token_required(f):
    """
    Decorator to ensure a valid token is present in the Authorization header.
    Injects the current_user object into the decorated function's arguments.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # Check for Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            # Check if it's a Bearer token
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            current_app.logger.warning("API Auth: Missing or invalid Authorization header format.")
            return jsonify(error="Missing or invalid token"), 401

        # Verify the token using the auth service
        user_id = auth_service.verify_token(token)

        if not user_id:
            # Avoid logging the full token for security, maybe just first few chars if needed
            token_preview = token[:10] + "..." if token else "None"
            current_app.logger.warning(f"API Auth: Invalid or expired token received: {token_preview}")
            return jsonify(error="Invalid or expired token"), 401

        # Token is valid, find the user
        try:
            from app import db
            current_user = db.session.get(User, user_id) # Efficient lookup by primary key
            if not current_user:
                    current_app.logger.error(f"API Auth: Valid token for non-existent user_id {user_id}")
                    return jsonify(error="Invalid token user"), 401
        except Exception as e:
            current_app.logger.error(f"API Auth: Error fetching user {user_id} from DB: {e}", exc_info=True)
            return jsonify(error="Internal server error during authentication"), 500

        current_app.logger.info(f"API Auth: Token verified for user: {current_user.username} (ID: {user_id})")
        # Inject the user object into the wrapped function
        return f(current_user, *args, **kwargs)

    return decorated_function
# --- End function definition ---

