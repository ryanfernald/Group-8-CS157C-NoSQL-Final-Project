# File: your_chat_project/app/services/message_service.py

import redis
import json
from datetime import datetime, timezone
from app import redis_client # Import redis_client
from app.models import User, ChatMember # Import necessary models
# Import more exceptions
from werkzeug.exceptions import Forbidden, InternalServerError, ServiceUnavailable

# Configuration for retrieval limit
DEFAULT_MESSAGE_LIMIT = 50

def send_message(sender: User, chat_id: int, content: str):
    """
    Sends a message by adding it to the Redis recent messages list for the chat.
    The Redis list is allowed to grow; trimming is handled by a separate flush task.
    """
    print(f"SERVICE: Attempting to send message by User ID {sender.user_id} to Chat ID {chat_id}")

    # --- Authorization Check: Verify sender is a member of the chat ---
    is_member = ChatMember.query.filter_by(user_id=sender.user_id, chat_id=chat_id).first()
    if not is_member:
        print(f"SERVICE: Send message failed - User {sender.user_id} is not a member of Chat {chat_id}")
        raise Forbidden("You are not a member of this chat.") # 403 Forbidden

    # --- Prepare Message Data ---
    timestamp_now = datetime.now(timezone.utc)
    timestamp_str = timestamp_now.isoformat(timespec='seconds').replace('+00:00', 'Z')

    message_data = {
        "sender_id": sender.user_id,
        "content": content,
        "created_at": timestamp_str
    }

    # --- Interact with Redis ---
    if not redis_client:
         print("ERROR: Redis client not initialized during message sending!")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis).") # 503

    try:
        redis_key = f"recent_messages:{chat_id}"
        message_json = json.dumps(message_data) # Convert dict to JSON string

        # --- Only LPUSH, no LTRIM ---
        list_length = redis_client.lpush(redis_key, message_json) # Add to the start of the list

        print(f"SERVICE: Message pushed to Redis list {redis_key}. New length: {list_length}.")

        return message_data # Return the data that was sent

    except redis.exceptions.ConnectionError as e:
         print(f"ERROR: Could not connect to Redis during message sending: {e}")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis connection).")
    except redis.exceptions.RedisError as e:
         print(f"ERROR: Redis error during message sending: {e}")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis error).")
    except Exception as e:
         print(f"ERROR: Unexpected error during message sending: {e}")
         raise InternalServerError("An unexpected error occurred while sending the message.")


# --- NEW FUNCTION TO GET RECENT MESSAGES ---
def get_recent_messages(requester: User, chat_id: int, limit: int = DEFAULT_MESSAGE_LIMIT):
    """
    Retrieves the most recent messages for a chat from the Redis cache.

    Args:
        requester: The User object making the request.
        chat_id: The ID of the chat to retrieve messages for.
        limit: The maximum number of messages to retrieve.

    Returns:
        A list of dictionaries, where each dictionary represents a message.

    Raises:
        Forbidden: If the requester is not a member of the chat.
        ServiceUnavailable: If Redis client is not available or connection fails.
        InternalServerError: For other unexpected errors.
    """
    print(f"SERVICE: Attempting to get recent messages for Chat ID {chat_id} by User ID {requester.user_id}")

    # --- Authorization Check: Verify requester is a member of the chat ---
    is_member = ChatMember.query.filter_by(user_id=requester.user_id, chat_id=chat_id).first()
    if not is_member:
        print(f"SERVICE: Get messages failed - User {requester.user_id} is not a member of Chat {chat_id}")
        raise Forbidden("You are not a member of this chat.") # 403 Forbidden

    # --- Interact with Redis ---
    if not redis_client:
         print("ERROR: Redis client not initialized during message retrieval!")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis).") # 503

    try:
        redis_key = f"recent_messages:{chat_id}"
        # Retrieve the latest 'limit' messages (0 to limit-1 because LPUSH adds to front)
        # LRANGE returns a list of strings (or bytes if decode_responses=False)
        messages_json_list = redis_client.lrange(redis_key, 0, limit - 1)

        # Parse the JSON strings back into Python dictionaries
        messages = []
        for msg_json in messages_json_list:
            try:
                messages.append(json.loads(msg_json))
            except json.JSONDecodeError:
                print(f"WARNING: Could not decode JSON from Redis for chat {chat_id}: {msg_json}")
                # Decide how to handle corrupted data - skip it for now
                continue

        print(f"SERVICE: Retrieved {len(messages)} recent messages from Redis for Chat ID {chat_id}")
        # Note: The list returned by LRANGE is newest-to-oldest because we use LPUSH
        # The client might need to reverse this if they want chronological order.
        return messages

    except redis.exceptions.ConnectionError as e:
         print(f"ERROR: Could not connect to Redis during message retrieval: {e}")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis connection).")
    except redis.exceptions.RedisError as e:
         print(f"ERROR: Redis error during message retrieval: {e}")
         raise ServiceUnavailable("Message service temporarily unavailable (Redis error).")
    except Exception as e:
         print(f"ERROR: Unexpected error during message retrieval: {e}")
         raise InternalServerError("An unexpected error occurred while retrieving messages.")

