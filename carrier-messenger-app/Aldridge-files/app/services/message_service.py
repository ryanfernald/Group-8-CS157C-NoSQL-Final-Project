# File: your_chat_project/app/services/message_service.py

import redis
import json
from datetime import datetime, timezone, timedelta # Import timedelta if needed for parsing
from dateutil import parser # Use dateutil for robust ISO timestamp parsing
from app import db, redis_client # Import db and redis_client
from app.models import User, ChatMember, Message # Import Message model
# Import more exceptions
from werkzeug.exceptions import Forbidden, InternalServerError, ServiceUnavailable, BadRequest

# Configuration for retrieval limit
DEFAULT_MESSAGE_LIMIT = 50

def send_message(sender: User, chat_id: int, content: str):
    """
    Sends a message by adding it to the Redis recent messages list for the chat.
    The Redis list is allowed to grow; trimming is handled by a separate flush task.
    """
    # (Code from previous step - remains the same)
    print(f"SERVICE: Attempting to send message by User ID {sender.user_id} to Chat ID {chat_id}")
    is_member = ChatMember.query.filter_by(user_id=sender.user_id, chat_id=chat_id).first()
    if not is_member:
        print(f"SERVICE: Send message failed - User {sender.user_id} is not a member of Chat {chat_id}")
        raise Forbidden("You are not a member of this chat.")
    timestamp_now = datetime.now(timezone.utc)
    timestamp_str = timestamp_now.isoformat(timespec='seconds').replace('+00:00', 'Z')
    message_data = { "sender_id": sender.user_id, "content": content, "created_at": timestamp_str }
    if not redis_client:
         print("ERROR: Redis client not initialized during message sending!")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis).")
    try:
        redis_key = f"recent_messages:{chat_id}"
        message_json = json.dumps(message_data)
        list_length = redis_client.lpush(redis_key, message_json)
        print(f"SERVICE: Message pushed to Redis list {redis_key}. New length: {list_length}.")
        return message_data
    except redis.exceptions.ConnectionError as e:
         print(f"ERROR: Could not connect to Redis during message sending: {e}")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis connection).")
    except redis.exceptions.RedisError as e:
         print(f"ERROR: Redis error during message sending: {e}")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis error).")
    except Exception as e:
         print(f"ERROR: Unexpected error during message sending: {e}")
         raise InternalServerError("An unexpected error occurred while sending the message.")


# --- MODIFIED FUNCTION TO GET MESSAGES (RECENT or OLDER) ---
def get_messages(requester: User, chat_id: int, before_timestamp_str: str = None, limit: int = DEFAULT_MESSAGE_LIMIT):
    """
    Retrieves messages for a chat.
    - If before_timestamp_str is None, retrieves the most recent messages from Redis.
    - If before_timestamp_str is provided, retrieves older messages from MySQL.

    Args:
        requester: The User object making the request.
        chat_id: The ID of the chat to retrieve messages for.
        before_timestamp_str: ISO 8601 timestamp string (optional). Fetch messages older than this.
        limit: The maximum number of messages to retrieve.

    Returns:
        A list of dictionaries, where each dictionary represents a message.

    Raises:
        Forbidden: If the requester is not a member of the chat.
        BadRequest: If the timestamp format is invalid.
        ServiceUnavailable: If Redis client is not available or connection fails (for recent).
        InternalServerError: For other unexpected errors.
    """
    print(f"SERVICE: Attempting to get messages for Chat ID {chat_id} by User ID {requester.user_id}. Before: {before_timestamp_str}, Limit: {limit}")

    # --- Authorization Check: Verify requester is a member of the chat ---
    is_member = ChatMember.query.filter_by(user_id=requester.user_id, chat_id=chat_id).first()
    if not is_member:
        print(f"SERVICE: Get messages failed - User {requester.user_id} is not a member of Chat {chat_id}")
        raise Forbidden("You are not a member of this chat.")

    # --- Decide Source: Redis (recent) or MySQL (older) ---
    if before_timestamp_str is None:
        # --- Fetch from Redis (Most Recent) ---
        print(f"SERVICE: Fetching recent messages from Redis for Chat ID {chat_id}")
        if not redis_client:
             print("ERROR: Redis client not initialized during message retrieval!")
             raise ServiceUnavailable("Message service temporarily unavailable (Redis).")
        try:
            redis_key = f"recent_messages:{chat_id}"
            messages_json_list = redis_client.lrange(redis_key, 0, limit - 1)
            messages = []
            for msg_json in messages_json_list:
                try:
                    messages.append(json.loads(msg_json))
                except json.JSONDecodeError:
                    print(f"WARNING: Could not decode JSON from Redis for chat {chat_id}: {msg_json}")
                    continue
            print(f"SERVICE: Retrieved {len(messages)} recent messages from Redis for Chat ID {chat_id}")
            # Note: Messages are newest-first from LRANGE
            return messages
        except redis.exceptions.ConnectionError as e:
             print(f"ERROR: Could not connect to Redis during message retrieval: {e}")
             raise ServiceUnavailable("Message service temporarily unavailable (Redis connection).")
        except redis.exceptions.RedisError as e:
             print(f"ERROR: Redis error during message retrieval: {e}")
             raise ServiceUnavailable("Message service temporarily unavailable (Redis error).")
        except Exception as e:
             print(f"ERROR: Unexpected error during Redis message retrieval: {e}")
             raise InternalServerError("An unexpected error occurred while retrieving recent messages.")

    else:
        # --- Fetch from MySQL (Older History) ---
        print(f"SERVICE: Fetching older messages from MySQL for Chat ID {chat_id} before {before_timestamp_str}")
        try:
            # Parse the ISO timestamp string into a datetime object
            # Use dateutil.parser for flexibility with timezone info (e.g., 'Z')
            before_timestamp = parser.isoparse(before_timestamp_str)
            # Ensure it's timezone-aware (UTC) if needed for comparison
            if before_timestamp.tzinfo is None:
                 # Or handle based on expected input format
                 raise ValueError("Timestamp must be timezone-aware")

        except (ValueError, TypeError) as e:
            print(f"ERROR: Invalid before_timestamp format: {before_timestamp_str} - {e}")
            raise BadRequest("Invalid 'before_timestamp' format. Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).")

        try:
            # Query MySQL for messages older than the timestamp
            query = Message.query.filter(
                Message.chat_id == chat_id,
                Message.created_at < before_timestamp
            ).order_by(Message.created_at.desc()).limit(limit)

            db_messages = query.all()

            # Format results into dictionaries
            messages = []
            for msg in db_messages:
                messages.append({
                    "message_id": msg.message_id, # Include the permanent ID from DB
                    "sender_id": msg.sender_id,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(timespec='seconds').replace('+00:00', 'Z')
                })

            print(f"SERVICE: Retrieved {len(messages)} older messages from MySQL for Chat ID {chat_id}")
            # Note: Messages are newest-first due to ORDER BY DESC
            return messages

        except Exception as e:
            print(f"ERROR: Unexpected error during MySQL message retrieval: {e}")
            # Log the full error e
            raise InternalServerError("An error occurred while retrieving older messages.")

