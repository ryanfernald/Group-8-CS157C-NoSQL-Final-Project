# File: your_chat_project/app/services/flush_service.py

import redis
import json
from datetime import datetime, timezone
from dateutil import parser
# from flask import current_app # No longer needed if using print
import traceback # To print tracebacks manually
from app import db, redis_client, scheduler # Import necessary instances
from app.models import Message # Import the Message model

# Configuration (Consider moving these to Config class)
FLUSH_BATCH_SIZE = 100 # How many messages to process per chat per run
SCAN_COUNT = 100 # How many keys to scan in Redis at a time

def find_message_keys():
    """Finds Redis keys matching the recent_messages pattern."""
    # Add print statements here too for debugging if needed
    print("FLUSH JOB: find_message_keys called.")
    if not redis_client:
         print("FLUSH JOB: find_message_keys - Redis client not available.")
         return []
    keys = set()
    cursor = '0'
    try:
        while cursor != 0:
            cursor, found_keys = redis_client.scan(cursor=cursor, match='recent_messages:*', count=SCAN_COUNT)
            print(f"FLUSH JOB: scan found keys: {found_keys}") # Debug scan results
            keys.update(found_keys)
            if cursor == b'0': # scan returns bytes for cursor '0'
                 break
    except Exception as e:
         print(f"FLUSH JOB: ERROR during redis scan: {e}")
         traceback.print_exc() # Print traceback for scan errors
         return [] # Return empty list on error
    print(f"FLUSH JOB: find_message_keys returning: {list(keys)}")
    return list(keys)

def flush_job():
    """
    The background job scheduled by APScheduler.
    Uses print() for logging.
    """
    print("--- FLUSH JOB FUNCTION CALLED ---")

    app = scheduler.app
    if not app:
         print("FLUSH JOB: ERROR - Could not get Flask app instance from scheduler.")
         return

    # App context is still needed for database operations
    with app.app_context():
        print("FLUSH JOB: Starting Redis to MySQL flush...") # Replaced logger

        if not redis_client:
            print("FLUSH JOB: Redis client not available. Aborting.") # Replaced logger
            return

        try:
            # 1. Find all 'recent_messages:<chat_id>' keys
            message_keys = find_message_keys()
            print(f"FLUSH JOB: Found {len(message_keys)} potential chat lists to process.") # Replaced logger

            for key in message_keys:
                # Add a print statement before the inner try block
                print(f"FLUSH JOB: Starting processing for key: {key}")
                try:
                    chat_id_str = key.split(':')[-1]
                    chat_id = int(chat_id_str)
                    print(f"FLUSH JOB: Processing key: {key} for chat_id: {chat_id}") # Replaced logger

                    # 2. Get a batch of messages from the END (oldest) of the list
                    messages_json_batch = redis_client.lrange(key, -FLUSH_BATCH_SIZE, -1)

                    if not messages_json_batch:
                        print(f"FLUSH JOB: No messages to flush for {key}") # Replaced logger
                        continue

                    messages_to_save = []
                    processed_indices = []

                    # 3. Parse JSON and prepare for DB insertion
                    print(f"FLUSH JOB: Parsing {len(messages_json_batch)} messages for {key}") # Added log
                    for i, msg_json in enumerate(messages_json_batch):
                        try:
                            msg_data = json.loads(msg_json)
                            created_at_dt = parser.isoparse(msg_data['created_at'])
                            new_db_message = Message(
                                chat_id=chat_id,
                                sender_id=msg_data['sender_id'],
                                content=msg_data['content'],
                                created_at=created_at_dt
                            )
                            messages_to_save.append(new_db_message)
                            processed_indices.append(i)

                        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as parse_err:
                            print(f"FLUSH JOB: Error parsing message JSON for key {key} at index {-FLUSH_BATCH_SIZE + i}: {msg_json}. Error: {parse_err}") # Replaced logger
                            continue

                    if not messages_to_save:
                        print(f"FLUSH JOB: No valid messages parsed for {key} in this batch.") # Replaced logger
                        continue

                    # 4. Save the batch to MySQL within a transaction
                    print(f"FLUSH JOB: Attempting to save {len(messages_to_save)} messages to MySQL for chat_id {chat_id}.") # Added log
                    try:
                        db.session.add_all(messages_to_save)
                        db.session.commit()
                        print(f"FLUSH JOB: Successfully saved {len(messages_to_save)} messages to MySQL for chat_id {chat_id}.") # Replaced logger

                        # 5. Remove the successfully saved messages from Redis
                        count_saved = len(messages_to_save)
                        redis_client.ltrim(key, 0, -(count_saved + 1))
                        print(f"FLUSH JOB: Trimmed {count_saved} messages from the end of Redis list {key}.") # Replaced logger

                    except Exception as db_err:
                        db.session.rollback()
                        print(f"FLUSH JOB: Database error saving messages for chat_id {chat_id}: {db_err}") # Replaced logger
                        traceback.print_exc() # Print full traceback for DB errors

                except ValueError:
                     print(f"FLUSH JOB: Could not parse chat_id from key: {key}") # Replaced logger
                     continue
                except redis.exceptions.RedisError as redis_err:
                     print(f"FLUSH JOB: Redis error processing key {key}: {redis_err}") # Replaced logger
                     continue
                except Exception as inner_err:
                     print(f"FLUSH JOB: Unexpected error processing key {key}: {inner_err}") # Replaced logger
                     traceback.print_exc() # Print full traceback
                     db.session.rollback() # Ensure rollback on unexpected errors too
                     continue

        except redis.exceptions.RedisError as redis_err:
            print(f"FLUSH JOB: Redis error during key scan: {redis_err}") # Replaced logger
        except Exception as e:
            print(f"FLUSH JOB: Unexpected error in main loop: {e}") # Replaced logger
            traceback.print_exc() # Print full traceback

        print("FLUSH JOB: Finished Redis to MySQL flush.") # Replaced logger

