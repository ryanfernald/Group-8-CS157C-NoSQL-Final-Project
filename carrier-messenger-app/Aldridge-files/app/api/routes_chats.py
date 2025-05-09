# File: your_chat_project/app/api/routes_chats.py

from flask import Blueprint, request, jsonify, current_app
# Import message_service along with chat_service
from app.services import chat_service, message_service
from app.utils.decorators import token_required # Import the decorator
from app.models import User # Import User for type hinting
# Import specific exceptions needed
from werkzeug.exceptions import BadRequest, NotFound, Forbidden, InternalServerError, ServiceUnavailable

# Create a Blueprint for chat routes
chats_bp = Blueprint('chats_bp', __name__, url_prefix='/chats')

# --- ROUTE TO GET USER'S CHATS ---
@chats_bp.route('', methods=['GET'])
@token_required # Requires user to be logged in
def get_user_chat_list(current_user: User):
    """
    Retrieves a list of chats the current user is a member of.
    """
    # (Code for getting chat list remains the same)
    current_app.logger.info(f"API: Received request to list chats for user: {current_user.username} (ID: {current_user.user_id})")
    try:
        chats = chat_service.get_user_chats(user=current_user)
        return jsonify(chats=chats), 200
    except Exception as e:
        current_app.logger.error(f"API: Unexpected error during chat list retrieval: {e}", exc_info=True)
        raise InternalServerError("An unexpected error occurred while retrieving chats.")


@chats_bp.route('', methods=['POST'])
@token_required
def create_new_chat(current_user: User):
    """ Creates a new chat (one-on-one or group). """
    # (Code for creating chat remains the same)
    current_app.logger.info(f"API: Received request to create chat by user: {current_user.username} (ID: {current_user.user_id})")
    data = request.get_json()
    if not data: raise BadRequest("Missing JSON request body.")
    if 'participant_ids' not in data or not isinstance(data['participant_ids'], list): raise BadRequest("Missing or invalid 'participant_ids' list.")
    if 'is_group' not in data or not isinstance(data['is_group'], bool): raise BadRequest("Missing or invalid 'is_group' boolean flag.")
    participant_ids = data['participant_ids']
    is_group = data['is_group']
    chat_name = data.get('chat_name')
    try:
        participant_ids = [int(pid) for pid in participant_ids if int(pid) != current_user.user_id]
    except ValueError:
        raise BadRequest("Participant IDs must be integers.")
    if is_group and not chat_name: raise BadRequest("Missing 'chat_name' for group chat.")
    try:
        new_chat = chat_service.create_chat(creator_user=current_user, participant_ids=participant_ids, is_group=is_group, chat_name=chat_name)
        response_data = { "message": "Chat created successfully", "chat": { "chat_id": new_chat.chat_id, "is_group_chat": new_chat.is_group_chat, "chat_name": new_chat.chat_name, "created_at": new_chat.created_at.isoformat() + 'Z' } }
        return jsonify(response_data), 201
    except (BadRequest, NotFound, Forbidden) as e:
        current_app.logger.warning(f"API: Chat creation failed ({e.code}): {e.description}")
        return jsonify(error=e.description), e.code
    except Exception as e:
        current_app.logger.error(f"API: Unexpected error during chat creation: {e}", exc_info=True)
        raise InternalServerError("An unexpected error occurred during chat creation.")


@chats_bp.route('/<int:chat_id>/messages', methods=['POST'])
@token_required
def send_chat_message(current_user: User, chat_id: int):
    """ Sends a message to a specific chat. """
    # (Code for sending message remains the same)
    current_app.logger.info(f"API: Received request to send message by User {current_user.user_id} to Chat {chat_id}")
    data = request.get_json()
    if not data or 'content' not in data or not data['content']: raise BadRequest("Missing or empty 'content' in request body.")
    content = data['content']
    try:
        sent_message_data = message_service.send_message(sender=current_user, chat_id=chat_id, content=content)
        return jsonify(message="Message sent successfully", message_data=sent_message_data), 201
    except Forbidden as e:
        current_app.logger.warning(f"API: Send message forbidden for User {current_user.user_id} in Chat {chat_id}: {e.description}")
        return jsonify(error=e.description), 403
    except ServiceUnavailable as e:
        current_app.logger.error(f"API: Send message failed due to service unavailable: {e.description}")
        return jsonify(error=e.description), 503
    except Exception as e:
        current_app.logger.error(f"API: Unexpected error during message sending to chat {chat_id}: {e}", exc_info=True)
        raise InternalServerError("An unexpected error occurred while sending the message.")


# --- MODIFIED ROUTE FOR GETTING MESSAGES ---
@chats_bp.route('/<int:chat_id>/messages', methods=['GET'])
@token_required # Requires user to be logged in
def get_chat_messages(current_user: User, chat_id: int):
    """
    Retrieves messages for a specific chat.
    Fetches recent from Redis if 'before_timestamp' is not provided.
    Fetches older from MySQL if 'before_timestamp' is provided.
    Optionally accepts 'limit' query parameter.
    """
    current_app.logger.info(f"API: Received request to get messages for Chat {chat_id} by User {current_user.user_id}")

    # Get optional query parameters
    before_timestamp_str = request.args.get('before_timestamp', None) # Get timestamp string or None
    limit_str = request.args.get('limit', str(message_service.DEFAULT_MESSAGE_LIMIT)) # Get limit string or default

    # Validate limit parameter
    try:
        limit = int(limit_str)
        if limit <= 0:
            raise ValueError("Limit must be positive.")
    except ValueError:
        raise BadRequest("Invalid 'limit' parameter. Must be a positive integer.")

    # --- Call Service ---
    try:
        # Call the unified get_messages service function, passing the timestamp string
        messages = message_service.get_messages(
            requester=current_user,
            chat_id=chat_id,
            before_timestamp_str=before_timestamp_str, # Pass the string or None
            limit=limit
        )
        # Return the list of messages
        # Note: Messages are returned newest-first
        return jsonify(messages=messages), 200 # 200 OK

    except Forbidden as e:
        current_app.logger.warning(f"API: Get messages forbidden for User {current_user.user_id} in Chat {chat_id}: {e.description}")
        return jsonify(error=e.description), 403
    except BadRequest as e: # Catch potential timestamp format error from service
         current_app.logger.warning(f"API: Bad request for getting messages for Chat {chat_id}: {e.description}")
         return jsonify(error=e.description), 400
    except ServiceUnavailable as e:
        current_app.logger.error(f"API: Get messages failed due to service unavailable: {e.description}")
        return jsonify(error=e.description), 503
    except Exception as e:
        current_app.logger.error(f"API: Unexpected error during message retrieval for chat {chat_id}: {e}", exc_info=True)
        raise InternalServerError("An unexpected error occurred while retrieving messages.")

