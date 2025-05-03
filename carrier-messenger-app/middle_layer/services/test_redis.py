import redis

def check_redis_connection():
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    print("🔍 All user tokens:")
    for key in r.scan_iter("user_token:*"):
        print(f"Key: {key}")
        print("Fields:", r.hgetall(key))
        print("TTL:", r.ttl(key), "seconds")
        print("-" * 40)

    print("🔍 All temp users:")
    for key in r.scan_iter("user:temp:*"):
        print(f"Key: {key}")
        print("Fields:", r.hgetall(key))
        print("-" * 40)

    print("🔍 All chat tokens:")
    for key in r.scan_iter("message_token:*"):
        print(f"Key: {key}")
        print("Fields:", r.hgetall(key))
        print("-" * 40)

    print("🔍 All temp chats:")
    for key in r.scan_iter("chat:temp:*"):
        print(f"Key: {key}")
        print("Fields:", r.hgetall(key))
        print("-" * 40)
        
if __name__ == "__main__":
    check_redis_connection()