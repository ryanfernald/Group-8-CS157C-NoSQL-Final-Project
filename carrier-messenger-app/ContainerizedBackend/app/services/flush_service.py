import redis
import json
from datetime import datetime, timezone
from dateutil import parser
import traceback
from app import db, redis_client, scheduler
from app.models import Message

FLUSH_BATCH_SIZE = 100
SCAN_COUNT = 100

# Scans Redis for keys that match recent_messages:* and returns them
def find_message_keys():
    print("FLUSH JOB: find_message_keys called.")
    if not redis_client:
        print("FLUSH JOB: find_message_keys - Redis client not available.")
        return []
    keys = set()
    cursor = '0'
    try:
        while cursor != 0:
            cursor, found_keys = redis_client.scan(cursor=cursor, match='recent_messages:*', count=SCAN_COUNT)
            print(f"FLUSH JOB: scan found keys: {found_keys}")
            keys.update(found_keys)
            if cursor == b'0':
                break
    except Exception as e:
        print(f"FLUSH JOB: ERROR during redis scan: {e}")
        traceback.print_exc()
        return []
    print(f"FLUSH JOB: find_message_keys returning: {list(keys)}")
    return list(keys)

# Scheduled background job that flushes Redis messages to the database
def flush_job():
    print("--- FLUSH JOB FUNCTION CALLED ---")
    app = scheduler.app
    if not app:
        print("FLUSH JOB: ERROR - Could not get Flask app instance from scheduler.")
        return

    with app.app_context():
        print("FLUSH JOB: Starting Redis to MySQL flush...")

        if not redis_client:
            print("FLUSH JOB: Redis client not available. Aborting.")
            return

        try:
            message_keys = find_message_keys()
            print(f"FLUSH JOB: Found {len(message_keys)} potential chat lists to process.")

            for key in message_keys:
                print(f"FLUSH JOB: Starting processing for key: {key}")
                try:
                    chat_id_str = key.split(':')[-1]
                    chat_id = int(chat_id_str)
                    print(f"FLUSH JOB: Processing key: {key} for chat_id: {chat_id}")

                    messages_json_batch = redis_client.lrange(key, -FLUSH_BATCH_SIZE, -1)

                    if not messages_json_batch:
                        print(f"FLUSH JOB: No messages to flush for {key}")
                        continue

                    messages_to_save = []
                    processed_indices = []

                    print(f"FLUSH JOB: Parsing {len(messages_json_batch)} messages for {key}")
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
                            print(f"FLUSH JOB: Error parsing message JSON for key {key} at index {-FLUSH_BATCH_SIZE + i}: {msg_json}. Error: {parse_err}")
                            continue

                    if not messages_to_save:
                        print(f"FLUSH JOB: No valid messages parsed for {key} in this batch.")
                        continue

                    print(f"FLUSH JOB: Attempting to save {len(messages_to_save)} messages to MySQL for chat_id {chat_id}.")
                    try:
                        db.session.add_all(messages_to_save)
                        db.session.commit()
                        print(f"FLUSH JOB: Successfully saved {len(messages_to_save)} messages to MySQL for chat_id {chat_id}.")
                        count_saved = len(messages_to_save)
                        redis_client.ltrim(key, 0, -(count_saved + 1))
                        print(f"FLUSH JOB: Trimmed {count_saved} messages from the end of Redis list {key}.")
                    except Exception as db_err:
                        db.session.rollback()
                        print(f"FLUSH JOB: Database error saving messages for chat_id {chat_id}: {db_err}")
                        traceback.print_exc()

                except ValueError:
                    print(f"FLUSH JOB: Could not parse chat_id from key: {key}")
                    continue
                except redis.exceptions.RedisError as redis_err:
                    print(f"FLUSH JOB: Redis error processing key {key}: {redis_err}")
                    continue
                except Exception as inner_err:
                    print(f"FLUSH JOB: Unexpected error processing key {key}: {inner_err}")
                    traceback.print_exc()
                    db.session.rollback()
                    continue

        except redis.exceptions.RedisError as redis_err:
            print(f"FLUSH JOB: Redis error during key scan: {redis_err}")
        except Exception as e:
            print(f"FLUSH JOB: Unexpected error in main loop: {e}")
            traceback.print_exc()

        print("FLUSH JOB: Finished Redis to MySQL flush.")
