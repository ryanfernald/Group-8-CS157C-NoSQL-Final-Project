# File: api_test_enhanced.py
# More thorough script to test the Flask Chat API endpoints

import requests
import json
import time
import random
import math
import uuid

# --- Configuration ---
BASE_URL = "http://localhost:5000" # Your Flask app URL
VERBOSE = False # Set to False to reduce log spam during bulk operations
NUM_USERS = 10 # Reduced for faster testing, increase if needed
NUM_CHATS_1ON1 = 5
NUM_CHATS_GROUP = 3
NUM_GROUP_MEMBERS_MIN = 3
NUM_GROUP_MEMBERS_MAX = 5 # Should be <= NUM_USERS
NUM_MESSAGES_PER_CHAT = 15 # Send a few messages to each chat
REQUEST_TIMEOUT = 20 # Slightly longer timeout

# --- Global Storage ---
users = [] # List to store {"id": user_id, "username": ..., "email": ..., "password": ..., "token": ...} # Added email here
chats = [] # List to store {"chat_id": ..., "is_group": ..., "members": [user_id, ...]}

# --- Helper Functions ---
def make_request(method, endpoint, data=None, headers=None):
    """Makes an HTTP request and returns the response object or None on error."""
    url = f"{BASE_URL}{endpoint}"
    log_prefix = f">>> Request: {method.upper()} {url}"
    try:
        response = requests.request(method, url, json=data, headers=headers, timeout=REQUEST_TIMEOUT)
        if VERBOSE:
            print(f"\n{log_prefix}")
            if headers:
                safe_headers = headers.copy()
                if 'Authorization' in safe_headers and len(safe_headers['Authorization']) > 20:
                        safe_headers['Authorization'] = safe_headers['Authorization'][:15] + "...'"
                print(f"    Headers: {safe_headers}")
            if data:
                print(f"    Data: {json.dumps(data)}")
            print(f"<<< Response: Status {response.status_code}")
            try:
                print(f"    Body: {response.json()}")
            except json.JSONDecodeError:
                print(f"    Body: (Not JSON) {response.text[:100]}...")
        return response
    except requests.exceptions.RequestException as e:
        print(f"\n{log_prefix}")
        print(f"!!! Request Error: {e}")
        return None

def check_status(response, expected_status, test_name="Test"):
    """Checks status and prints pass/fail."""
    status = response.status_code if response is not None else "No Response"
    result = "Passed" if response is not None and status == expected_status else "Failed"
    print(f"--- Test: {test_name} ---")
    print(f"    Expected: {expected_status}, Got: {status} -> {result}")
    if result == "Failed":
        if response is not None:
            try:
                print(f"    Error Body: {response.json()}")
            except json.JSONDecodeError:
                    print(f"    Error Body: {response.text}")
        return False
    return True

def register_user(username, email, password):
    """Registers a single user."""
    user_data = {"username": username, "email": email, "password": password}
    resp = make_request("POST", "/auth/register", data=user_data)
    if check_status(resp, 201, f"Register User '{username}'"):
        user_info = resp.json().get('user', {})
        user_id = user_info.get('user_id')
        if user_id:
            # --- FIX: Add email to the stored user dictionary ---
            users.append({
                "id": user_id,
                "username": username,
                "email": email, # Added email
                "password": password,
                "token": None
            })
            # ----------------------------------------------------
            return user_id
    return None

def login_user(username, password):
    """Logs in a user and returns the token."""
    login_data = {"username": username, "password": password}
    resp = make_request("POST", "/auth/login", data=login_data)
    if check_status(resp, 200, f"Login User '{username}'"):
        token = resp.json().get("token")
        # Update token in global users list
        for user in users:
            if user["username"] == username:
                user["token"] = token
                break
        return token
    return None

def get_auth_headers(user_id):
    """Gets the Authorization header for a user."""
    user = next((u for u in users if u["id"] == user_id), None)
    if user and user["token"]:
        return {"Authorization": f"Bearer {user['token']}"}
    print(f"!!! Warning: Could not find token for user {user_id}")
    return None

def create_chat(creator_id, participant_ids, is_group, chat_name=None):
    """Creates a chat."""
    headers = get_auth_headers(creator_id)
    if not headers: return None
    chat_data = {"participant_ids": participant_ids, "is_group": is_group}
    if chat_name:
        chat_data["chat_name"] = chat_name
    resp = make_request("POST", "/chats", data=chat_data, headers=headers)
    test_name = f"Create Chat (Creator: {creator_id}, Group: {is_group})"
    if check_status(resp, 201, test_name):
        chat_info = resp.json().get("chat", {})
        chat_id = chat_info.get("chat_id")
        if chat_id:
                all_members = [creator_id] + participant_ids
                chats.append({"chat_id": chat_id, "is_group": is_group, "members": all_members})
                return chat_id
    return None

def send_message(sender_id, chat_id, content):
        """Sends a message."""
        headers = get_auth_headers(sender_id)
        if not headers: return None
        message_data = {"content": content}
        endpoint = f"/chats/{chat_id}/messages"
        resp = make_request("POST", endpoint, data=message_data, headers=headers)
        # Don't fail script on message send failure, just check status
        check_status(resp, 201, f"Send Msg (User {sender_id} -> Chat {chat_id})")
        return resp

def get_messages(retriever_id, chat_id, limit=None, before_ts=None):
    """Gets messages for a chat."""
    headers = get_auth_headers(retriever_id)
    if not headers: return None
    endpoint = f"/chats/{chat_id}/messages"
    params = {}
    if limit: params['limit'] = limit
    if before_ts: params['before_timestamp'] = before_ts
    # requests library handles query params from a dict
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT) # Use requests directly to pass params easily
    test_suffix = f"before {before_ts}" if before_ts else "recent"
    if check_status(resp, 200, f"Get Msgs (User {retriever_id}, Chat {chat_id}, {test_suffix})"):
        return resp.json().get("messages", [])
    return None


# --- Test Execution ---
print("="*20 + " STARTING ENHANCED API TESTS " + "="*20)
print(f"Config: {NUM_USERS} Users, {NUM_CHATS_1ON1} 1-1 Chats, {NUM_CHATS_GROUP} Group Chats, ~{NUM_MESSAGES_PER_CHAT} Msgs/Chat")

# === Phase 1: User Registration and Login ===
print("\n" + "="*10 + " Phase 1: Registration & Login " + "="*10)
# Register users
for i in range(NUM_USERS):
    register_user(f"testuser{i}", f"user{i}@test.com", f"password{i}")
assert len(users) == NUM_USERS, "Failed to register all users"
print(f"--- Registered {len(users)} users ---")

# Test duplicate registration
print("\n--- Testing Duplicate Registration ---")
# Use the correct keys now, including email
resp_dup = register_user(users[0]['username'], users[0]['email'], users[0]['password'])
assert resp_dup is None, "Duplicate registration should fail" # check_status is called inside helper

# Login users
print("\n--- Testing Login ---")
for user in users:
    login_user(user['username'], user['password'])
assert all(u['token'] is not None for u in users), "Failed to log in all users"
print(f"--- Logged in {len(users)} users ---")

# Test invalid login
print("\n--- Testing Invalid Login ---")
token_invalid = login_user(users[0]['username'], "wrongpassword")
assert token_invalid is None, "Login with wrong password should fail"
token_nonexist = login_user("nonexistentuser", "password")
assert token_nonexist is None, "Login with non-existent user should fail"

# === Phase 2: Chat Creation ===
print("\n" + "="*10 + " Phase 2: Chat Creation " + "="*10)
# Create 1-on-1 chats
print(f"\n--- Creating {NUM_CHATS_1ON1} 1-on-1 Chats ---")
created_pairs = set()
created_1on1_count = 0
attempts = 0
while created_1on1_count < NUM_CHATS_1ON1 and attempts < NUM_CHATS_1ON1 * 5:
    attempts += 1
    user1, user2 = random.sample(users, 2)
    pair = tuple(sorted((user1["id"], user2["id"])))
    if pair in created_pairs: continue
    chat_id = create_chat(user1["id"], [user2["id"]], is_group=False)
    if chat_id:
        created_pairs.add(pair)
        created_1on1_count += 1
    time.sleep(0.05)
print(f"--- Created {created_1on1_count} 1-on-1 chats ---")

# Create Group chats
print(f"\n--- Creating {NUM_CHATS_GROUP} Group Chats ---")
created_group_count = 0
attempts = 0
while created_group_count < NUM_CHATS_GROUP and attempts < NUM_CHATS_GROUP * 5:
    attempts += 1
    creator = random.choice(users)
    num_members = random.randint(NUM_GROUP_MEMBERS_MIN - 1, NUM_GROUP_MEMBERS_MAX - 1)
    other_users = [u for u in users if u["id"] != creator["id"]]
    if len(other_users) < num_members: continue
    participants = random.sample(other_users, num_members)
    participant_ids = [p["id"] for p in participants]
    chat_name = f"Test Group #{created_group_count + 1}"
    chat_id = create_chat(creator["id"], participant_ids, is_group=True, chat_name=chat_name)
    if chat_id:
        created_group_count += 1
    time.sleep(0.05)
print(f"--- Created {created_group_count} group chats ---")

# Test invalid chat creation
print("\n--- Testing Invalid Chat Creation ---")
# No participants
resp_no_parts = make_request("POST", "/chats", data={"participant_ids": [], "is_group": False}, headers=get_auth_headers(users[0]['id']))
check_status(resp_no_parts, 400, "Create Chat No Participants")
# Group without name
resp_no_name = make_request("POST", "/chats", data={"participant_ids": [users[1]['id']], "is_group": True}, headers=get_auth_headers(users[0]['id']))
check_status(resp_no_name, 400, "Create Group No Name")
# Non-existent participant
resp_bad_part = make_request("POST", "/chats", data={"participant_ids": [99999], "is_group": False}, headers=get_auth_headers(users[0]['id']))
check_status(resp_bad_part, 404, "Create Chat Bad Participant")

# === Phase 3: List Chats ===
print("\n" + "="*10 + " Phase 3: List Chats " + "="*10)
if users:
    user_to_check = random.choice(users)
    print(f"\n--- Listing chats for User {user_to_check['id']} ---")
    headers = get_auth_headers(user_to_check['id'])
    resp = make_request("GET", "/chats", headers=headers)
    if check_status(resp, 200, f"List Chats User {user_to_check['id']}"):
        user_chats = resp.json().get('chats', [])
        print(f"    User {user_to_check['id']} found in {len(user_chats)} chats.")
        # Verify user is actually a member of returned chats
        for chat_info in user_chats:
            member_ids = [m['user_id'] for m in chat_info.get('members', [])]
            assert user_to_check['id'] in member_ids, f"User {user_to_check['id']} not found in members of chat {chat_info.get('chat_id')}"
        print("    Membership verified in listed chats.")
else:
    print("!!! No users available to test List Chats.")

# === Phase 4: Sending Messages ===
print("\n" + "="*10 + " Phase 4: Sending Messages " + "="*10)
messages_sent_count = 0
if not chats:
    print("!!! No chats created, skipping message sending.")
else:
    print(f"\n--- Sending ~{NUM_MESSAGES_PER_CHAT} messages to each chat ---")
    for chat in chats:
        chat_id = chat["chat_id"]
        member_ids = chat["members"]
        print(f"  -> Sending to Chat {chat_id} (Members: {member_ids})")
        for i in range(NUM_MESSAGES_PER_CHAT):
            sender_id = random.choice(member_ids)
            content = f"Chat {chat_id} - Msg {i+1} by User {sender_id} - {uuid.uuid4().hex[:8]}"
            resp = send_message(sender_id, chat_id, content)
            if resp and resp.status_code == 201:
                messages_sent_count += 1
            time.sleep(0.01) # Very small delay
    print(f"--- Sent {messages_sent_count} messages ---")

# Test invalid message sending
print("\n--- Testing Invalid Message Sending ---")
if users and chats:
    user_not_in_chat = users[0]
    chat_to_test = chats[-1] # Pick last chat
    # Make sure user_not_in_chat is definitely not in chat_to_test members
    if user_not_in_chat['id'] not in chat_to_test['members']:
            resp_forbidden = send_message(user_not_in_chat['id'], chat_to_test['chat_id'], "I shouldn't be here!")
            check_status(resp_forbidden, 403, "Send Msg Not Member")
    else:
            print("    Skipping 'Not Member' test - user was randomly in the chat.")

    # Send empty message
    resp_empty = send_message(chat_to_test['members'][0], chat_to_test['chat_id'], "")
    check_status(resp_empty, 400, "Send Empty Msg")
    # Send to non-existent chat
    resp_no_chat = send_message(users[0]['id'], 99999, "Hello?")
    check_status(resp_no_chat, 403, "Send Msg Bad Chat ID") # Expect 403 as user isn't member

else:
        print("!!! Skipping invalid message tests - need users and chats.")

# === Phase 5: Retrieving Messages ===
print("\n" + "="*10 + " Phase 5: Retrieving Messages " + "="*10)
if not chats:
        print("!!! No chats to test retrieval.")
else:
    # Pick a random chat to test thoroughly
    chat_to_test = random.choice(chats)
    retriever_id = random.choice(chat_to_test['members'])
    print(f"\n--- Testing retrieval for Chat {chat_to_test['chat_id']} by User {retriever_id} ---")

    # Get recent messages (default limit)
    recent_messages = get_messages(retriever_id, chat_to_test['chat_id'])
    assert recent_messages is not None, "Failed to get recent messages"
    print(f"    Retrieved {len(recent_messages)} recent messages (default limit).")
    if recent_messages:
        oldest_ts_in_recent = recent_messages[-1].get("created_at")
        print(f"    Oldest timestamp in recent batch: {oldest_ts_in_recent}")

        # Get older messages (will likely be empty unless flush job ran)
        print(f"--- Testing Older Messages (before {oldest_ts_in_recent}) ---")
        older_messages = get_messages(retriever_id, chat_to_test['chat_id'], before_ts=oldest_ts_in_recent)
        assert older_messages is not None, "Failed to get older messages"
        print(f"    Retrieved {len(older_messages)} older messages (likely 0 if flush hasn't run).")

        # Test invalid timestamp format
        print("--- Testing Invalid Timestamp ---")
        resp_bad_ts = make_request("GET", f"/chats/{chat_to_test['chat_id']}/messages?before_timestamp=invalid-date", headers=get_auth_headers(retriever_id))
        check_status(resp_bad_ts, 400, "Get Msgs Bad Timestamp")

    # Test retrieval limits
    print("--- Testing Limit Parameter ---")
    limited_messages = get_messages(retriever_id, chat_to_test['chat_id'], limit=3)
    assert limited_messages is not None, "Failed to get limited messages"
    assert len(limited_messages) <= 3, f"Expected max 3 messages with limit=3, got {len(limited_messages)}"
    print(f"    Retrieved {len(limited_messages)} messages with limit=3.")

    # Test retrieval by user not in chat
    if len(users) > len(chat_to_test['members']):
            user_not_in_chat = next((u for u in users if u['id'] not in chat_to_test['members']), None)
            if user_not_in_chat:
                print("--- Testing Get Msgs Not Member ---")
                resp_forbidden = make_request("GET", f"/chats/{chat_to_test['chat_id']}/messages", headers=get_auth_headers(user_not_in_chat['id']))
                check_status(resp_forbidden, 403, "Get Msgs Not Member")

print("\n" + "="*20 + " FINISHED ENHANCED API TESTS " + "="*20)
