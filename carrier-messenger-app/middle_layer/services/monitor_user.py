import redis
from flush_users_to_mysql import flush_user_to_mysql
from retrieve_chats_for_user import hydrate_user_chats

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def monitor_user_tokens():
    pubsub = r.pubsub()
    pubsub.psubscribe('__keyevent@0__:expired', '__keyspace@0__:user_token:*')

    print("🔄 Monitoring for user login/logout events...")
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            event_key = message['channel']
            redis_key = message['data']

            # Handle token expiration
            if redis_key.startswith("user_token:tk") and 'expired' in event_key:
                user_id = redis_key.replace("user_token:tk", "")
                flush_user_to_mysql(user_id)

            # Handle login (HSET triggers keyspace, not keyevent)
            elif redis_key.startswith("user_token:tk") and 'keyspace' in event_key:
                user_id = redis_key.replace("user_token:tk", "")
                hydrate_user_chats(user_id)

if __name__ == "__main__":
    monitor_user_tokens()