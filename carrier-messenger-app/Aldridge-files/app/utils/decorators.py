from functools import wraps
from flask import request, jsonify, current_app
from app.services import auth_service
from app.models import User

# Decorator that verifies token and injects the authenticated user into route handlers
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            current_app.logger.warning("API Auth: Missing or invalid Authorization header format.")
            return jsonify(error="Missing or invalid token"), 401

        user_id = auth_service.verify_token(token)

        if not user_id:
            token_preview = token[:10] + "..." if token else "None"
            current_app.logger.warning(f"API Auth: Invalid or expired token received: {token_preview}")
            return jsonify(error="Invalid or expired token"), 401

        try:
            from app import db
            current_user = db.session.get(User, user_id)
            if not current_user:
                current_app.logger.error(f"API Auth: Valid token for non-existent user_id {user_id}")
                return jsonify(error="Invalid token user"), 401
        except Exception as e:
            current_app.logger.error(f"API Auth: Error fetching user {user_id} from DB: {e}", exc_info=True)
            return jsonify(error="Internal server error during authentication"), 500

        current_app.logger.info(f"API Auth: Token verified for user: {current_user.username} (ID: {user_id})")
        return f(current_user, *args, **kwargs)

    return decorated_function
