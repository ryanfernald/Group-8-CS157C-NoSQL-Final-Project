import requests
import json
import re
import time
import uuid

# Configures constants and global storage
API_BASE_URL = "http://localhost:5000"
TEXT_FILE_PATH = "1524-0.txt"
VERBOSE_LOGGING = True
API_DELAY = 0.02
SKIP_ACT_SCENE_LINES = True

registered_characters = {}
active_1on1_chats = {}

# Logs API or parser actions to console
def log_action(message):
    if VERBOSE_LOGGING:
        print(f"[LOG] {message}")

# Sends an API request with retry, logging, and rate limiting
def api_call(method, endpoint, data=None, headers=None, attempt=1, max_attempts=3):
    url = f"{API_BASE_URL}{endpoint}"
    log_action(f"API Call ({attempt}/{max_attempts}): {method} {url}")
    if data:
        log_action(f"  Data: {json.dumps(data)}")
    if headers:
        safe_headers = headers.copy()
        if 'Authorization' in safe_headers and len(safe_headers['Authorization']) > 20:
            safe_headers['Authorization'] = safe_headers['Authorization'][:15] + "...'"
        log_action(f"  Headers: {safe_headers}")

    try:
        response = requests.request(method, url, json=data, headers=headers, timeout=30)
        log_action(f"  Response: {response.status_code}")
        if VERBOSE_LOGGING and response.content:
            try:
                log_action(f"    Body: {response.json()}")
            except json.JSONDecodeError:
                log_action(f"    Body (text): {response.text[:100]}...")
        time.sleep(API_DELAY)
        return response
    except requests.exceptions.RequestException as e:
        log_action(f"  !!! API Call Error: {e}")
        if attempt < max_attempts:
            log_action(f"  Retrying in {API_DELAY * 5} seconds...")
            time.sleep(API_DELAY * 5)
            return api_call(method, endpoint, data=data, headers=headers, attempt=attempt + 1, max_attempts=max_attempts)
        return None

# Registers a new character and logs them in to get a token
def register_character(character_name_raw):
    character_name = character_name_raw.strip().upper()
    if not character_name or character_name in ["PROLOGUE", "EPILOGUE"]:
        return None

    if character_name in registered_characters and registered_characters[character_name].get("token"):
        return registered_characters[character_name]

    log_action(f"Attempting to register character: '{character_name}'")
    email_safe_name = re.sub(r'\W+', '', character_name.lower())
    email = f"{email_safe_name}_{uuid.uuid4().hex[:4]}@hamlet.dk"
    password = f"password_{character_name.lower()}"

    reg_data = {"username": character_name, "email": email, "password": password}
    reg_response = api_call("POST", "/auth/register", data=reg_data)

    if reg_response and reg_response.status_code == 201:
        user_id = reg_response.json().get("user", {}).get("user_id")
        log_action(f"Successfully registered '{character_name}' with user_id: {user_id}")
        registered_characters[character_name] = {"user_id": user_id, "email": email, "password": password, "token": None}
    elif reg_response and reg_response.status_code == 409:
        log_action(f"Character '{character_name}' likely already exists (409). Attempting login.")
    else:
        log_action(f"Failed to register '{character_name}'. Status: {reg_response.status_code if reg_response else 'No Response'}")
        return None

    login_data = {"username": character_name, "password": password}
    login_response = api_call("POST", "/auth/login", data=login_data)
    if login_response and login_response.status_code == 200:
        token = login_response.json().get("token")
        if character_name in registered_characters and registered_characters[character_name].get("user_id"):
            registered_characters[character_name]["token"] = token
            log_action(f"Successfully logged in '{character_name}'.")
            return registered_characters[character_name]
        else:
            if character_name not in registered_characters:
                registered_characters[character_name] = {}
            registered_characters[character_name]["token"] = token
            log_action(f"Logged in existing user '{character_name}' (token obtained). User ID might be missing if registration was 409.")
            verify_headers = {"Authorization": f"Bearer {token}"}
            verify_response = api_call("GET", "/auth/verify", headers=verify_headers)
            if verify_response and verify_response.status_code == 200:
                user_id_from_verify = verify_response.json().get("user_id")
                if user_id_from_verify:
                    registered_characters[character_name]["user_id"] = user_id_from_verify
                    log_action(f"Updated user_id for '{character_name}' to {user_id_from_verify} via token verify.")
                    return registered_characters[character_name]
            log_action(f"WARNING: Logged in '{character_name}' but user_id is unknown. Cannot initiate chats robustly.")
            return None
    log_action(f"Failed to log in '{character_name}'. Status: {login_response.status_code if login_response else 'No Response'}")
    return None

# Creates or retrieves a private 1-on-1 chat between two registered users
def get_or_create_1on1_chat(user1_details, user2_details):
    if not user1_details or not user2_details or \
       "user_id" not in user1_details or "user_id" not in user2_details or \
       "token" not in user1_details:
        log_action("Cannot create chat: missing user details, ID, or token.")
        return None

    user1_id = user1_details["user_id"]
    user2_id = user2_details["user_id"]
    user1_token = user1_details["token"]

    if user1_id == user2_id:
        return None

    chat_pair_key = tuple(sorted((user1_id, user2_id)))
    if chat_pair_key in active_1on1_chats:
        return active_1on1_chats[chat_pair_key]

    log_action(f"Creating 1-on-1 chat between User {user1_id} and User {user2_id}")
    chat_data = {"participant_ids": [user2_id], "is_group": False}
    headers = {"Authorization": f"Bearer {user1_token}"}
    chat_response = api_call("POST", "/chats", data=chat_data, headers=headers)

    if chat_response and chat_response.status_code == 201:
        chat_id = chat_response.json().get("chat", {}).get("chat_id")
        if chat_id:
            log_action(f"Chat created successfully with ID: {chat_id}")
            active_1on1_chats[chat_pair_key] = chat_id
            return chat_id
    elif chat_response and chat_response.status_code == 400:
        log_action(f"Chat creation returned 400. Possibly already exists or bad request for {user1_id}-{user2_id}.")
    else:
        log_action(f"Failed to create chat for {user1_id}-{user2_id}. Status: {chat_response.status_code if chat_response else 'No Response'}")
    return None

# Sends a message to the given chat using the speaker's token
def send_message_to_chat(chat_id, sender_token, content):
    if not content or not sender_token:
        return False
    log_action(f"Sending message to Chat {chat_id}: '{content[:50]}...'")
    message_data = {"content": content.strip()}
    headers = {"Authorization": f"Bearer {sender_token}"}
    response = api_call("POST", f"/chats/{chat_id}/messages", data=message_data, headers=headers)
    return response and response.status_code == 201

# Extracts and registers characters from the Dramatis Personae section
def parse_dramatis_personae(lines):
    print("--- PARSING DRAMATIS PERSONAE ---")
    log_action("Parsing Dramatis Personae...")
    in_dramatis_section = False
    character_names = []
    char_regex = re.compile(r"^([A-Z][A-Z\s\-\']{2,})(?:,.*)?$")

    for line_num, line_content in enumerate(lines):
        line_strip = line_content.strip()
        if "Dramatis Personæ" in line_strip or "Characters in the Play" in line_strip:
            in_dramatis_section = True
            log_action(f"Dramatis Personae section started at line {line_num + 1}")
            continue
        if in_dramatis_section:
            if not line_strip:
                next_content_line_index = -1
                for k in range(lines.index(line_content) + 1, len(lines)):
                    if lines[k].strip():
                        next_content_line_index = k
                        break
                if next_content_line_index != -1 and any(marker in lines[next_content_line_index] for marker in ["SCENE.", "ACT I", "PROLOGUE"]):
                    log_action(f"Dramatis Personae section ended at line {line_num + 1} due to upcoming marker.")
                    break

            match = char_regex.match(line_strip)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'\b(KING|QUEEN|PRINCE|DUKE|LORD|LADY|SIR|MISTRESS)\b', '', name, flags=re.IGNORECASE).strip()
                name = re.sub(r'\s*OF\s*[A-Z\s]+$', '', name, flags=re.IGNORECASE).strip()
                name = name.title()
                if name and name.upper() not in ["SCENE", "CONTENTS", "ACT"] and len(name) > 1:
                    character_names.append(name.upper())

    unique_names = sorted(list(set(character_names)))
    log_action(f"Found characters in Dramatis Personae: {unique_names}")
    if not unique_names:
        print("--- NO CHARACTERS FOUND IN DRAMATIS PERSONAE ---")
    for name in unique_names:
        register_character(name)
    log_action("Finished pre-registering characters from Dramatis Personae.")

# Parses the entire play and simulates chat between characters
def process_play_text(file_path):
    print("--- PROCESS_PLAY_TEXT FUNCTION CALLED ---")
    log_action(f"Starting to process play text: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"--- Successfully read {len(lines)} lines from {file_path} ---")
    except FileNotFoundError:
        log_action(f"Error: File not found at {file_path}")
        print(f"--- FILE NOT FOUND: {file_path} ---")
        return

    dramatis_personae_end_index = 0
    found_dramatis_start = False
    for i, line in enumerate(lines):
        if "Dramatis Personæ" in line or "Characters in the Play" in line:
            found_dramatis_start = True
            log_action(f"Found Dramatis Personae start at line {i}")
            for j in range(i, len(lines)):
                if "ACT I" in lines[j] or "PROLOGUE" in lines[j] or "SCENE I." in lines[j] or \
                   (lines[j].strip() == "" and j+1 < len(lines) and ("ACT I" in lines[j+1] or "PROLOGUE" in lines[j+1] or "SCENE I." in lines[j+1])):
                    dramatis_personae_end_index = j
                    log_action(f"Dramatis Personae section estimated to end at line {j}")
                    break
            else:
                dramatis_personae_end_index = len(lines)
                log_action(f"Dramatis Personae section potentially goes to end of file.")
            if dramatis_personae_end_index > i:
                parse_dramatis_personae(lines[i:dramatis_personae_end_index])
            break
    if not found_dramatis_start:
        print("--- DRAMATIS PERSONAE SECTION NOT FOUND ---")

    character_line_regex = re.compile(r"^\s*([A-Z][A-Za-z\s\-\'\.]+)\.\s*$")
    stage_direction_regex = re.compile(r"^\s*\[.*?\]\s*$")
    scene_act_regex = re.compile(r"^\s*(ACT\s+[IVXLCDM]+|SCENE\s+[IVXLCDM]+|PROLOGUE|EPILOGUE)\b", re.IGNORECASE)

    current_speaker_name = None
    previous_speaker_name = None
    current_dialogue_lines = []
    current_chat_id = None

    start_line_index = dramatis_personae_end_index if dramatis_personae_end_index > 0 else 0
    print(f"--- Starting main dialogue parsing from line {start_line_index} ---")

    for i in range(start_line_index, len(lines)):
        line = lines[i]
        stripped_line = line.strip()

        if not stripped_line:
            continue

        if SKIP_ACT_SCENE_LINES and scene_act_regex.match(stripped_line):
            if current_speaker_name and current_dialogue_lines and current_chat_id:
                sender_details = registered_characters.get(current_speaker_name)
                if sender_details and sender_details.get("token"):
                    send_message_to_chat(current_chat_id, sender_details["token"], " ".join(current_dialogue_lines))
            current_dialogue_lines = []
            continue

        if stage_direction_regex.match(stripped_line):
            if current_speaker_name and current_dialogue_lines and current_chat_id:
                sender_details = registered_characters.get(current_speaker_name)
                if sender_details and sender_details.get("token"):
                    send_message_to_chat(current_chat_id, sender_details["token"], " ".join(current_dialogue_lines))
            current_dialogue_lines = []
            if "[_Exit" in stripped_line or "[_Exeunt" in stripped_line:
                current_speaker_name = None
            continue

        char_match = character_line_regex.match(stripped_line)

        if char_match:
            new_speaker_name_raw = char_match.group(1).strip().upper()
            if new_speaker_name_raw not in registered_characters:
                if len(new_speaker_name_raw) > 1 and new_speaker_name_raw.isupper() and new_speaker_name_raw not in ["ACT", "SCENE"]:
                    char_details = register_character(new_speaker_name_raw)
                    if not char_details:
                        if current_speaker_name: current_dialogue_lines.append(stripped_line)
                        continue
                else:
                    if current_speaker_name: current_dialogue_lines.append(stripped_line)
                    continue

            if current_speaker_name and current_speaker_name != new_speaker_name_raw:
                if current_dialogue_lines and current_chat_id:
                    sender_details = registered_characters.get(current_speaker_name)
                    if sender_details and sender_details.get("token"):
                        send_message_to_chat(current_chat_id, sender_details["token"], " ".join(current_dialogue_lines))
                current_dialogue_lines = []
                previous_speaker_name = current_speaker_name

            current_speaker_name = new_speaker_name_raw

            if previous_speaker_name and current_speaker_name != previous_speaker_name:
                user1_details = registered_characters.get(previous_speaker_name)
                user2_details = registered_characters.get(current_speaker_name)
                if user1_details and user2_details and user1_details.get("user_id") and user2_details.get("user_id"):
                    chat_id = get_or_create_1on1_chat(user1_details, user2_details)
                    current_chat_id = chat_id if chat_id else None
                else:
                    current_chat_id = None
            elif not previous_speaker_name and current_speaker_name:
                previous_speaker_name = current_speaker_name
                current_chat_id = None
        elif current_speaker_name:
            dialogue_part = line.strip()
            if dialogue_part:
                current_dialogue_lines.append(dialogue_part)

    if current_speaker_name and current_dialogue_lines and current_chat_id:
        sender_details = registered_characters.get(current_speaker_name)
        if sender_details and sender_details.get("token"):
            send_message_to_chat(current_chat_id, sender_details["token"], " ".join(current_dialogue_lines))

    log_action("Finished processing play text.")
    print("--- FINAL REGISTERED CHARACTERS ---")
    print(json.dumps(registered_characters, indent=2))
    print("--- FINAL ACTIVE 1-ON-1 CHATS ---")
    print(json.dumps(active_1on1_chats, indent=2, default=str))

# Entry point for running the parser when the script is executed
if __name__ == "__main__":
    print("--- SCRIPT START ---")
    print("Ensure your Flask backend API (http://localhost:5000) is running in Docker.")
    input("Press Enter to start the Hamlet parser and API interaction script...")
    print("--- STARTING PARSING ---")
    process_play_text(TEXT_FILE_PATH)
    print("\nScript finished. Check API logs, RedisInsight, and MySQL Workbench for results.")
