import redis
from flush_chat_to_mysql import flush_chat_to_mysql

def listen_for_chat_expiry():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    pubsub.psubscribe('__keyevent@0__:expired')

    print("🔄 Listening for expired chat tokens...")
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            expired_key = message['data']
            if expired_key.startswith("message_token:"):
                chat_id = expired_key.replace("message_token:", "")
                flush_chat_to_mysql(chat_id)

if __name__ == "__main__":
    listen_for_chat_expiry()