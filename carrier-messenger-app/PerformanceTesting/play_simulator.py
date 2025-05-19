# File: play_simulator.py
# This script parses a play and simulates chat interactions using my API.

import requests
import json
import re
import time
import uuid
import os
import traceback
import random

# Configuration settings for the simulation.
API_BASE_URL = "http://localhost:5000"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEXT_FILE_NAME = "pg2242.txt"
TEXT_FILE_PATH = os.path.join(SCRIPT_DIR, TEXT_FILE_NAME)
VERBOSE_SIMULATION_LOGS = True
DEBUG_API_CALLS = False
API_DELAY = 0
SKIP_ACT_SCENE_LINES = True
SIMULATE_READING_AFTER_SEND = True
SIMULATE_HISTORICAL_READING_END = True
MAX_HISTORICAL_READS_PER_CHAT = 2
DELAY_BETWEEN_READ_ACTIONS = 0.001

# Global storage for characters and chats.
registered_characters = {}
active_1on1_chats = {}
active_group_chats = {}

# Logs high-level simulation actions.
def log_sim_action(actor, action, details=""):
    if VERBOSE_SIMULATION_LOGS:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        actor_str = actor if isinstance(actor, str) else "SCRIPT_ERROR"
        details_str = f" ({details})" if details else ""
        print(f"[{timestamp}] SIM EVENT: Actor='{actor_str}', Action='{action}'{details_str}")

# Makes API calls, with retry logic for token expiration.
def api_call(method, endpoint, data=None, headers=None, character_details_for_retry=None, original_call_args=None):
    url = f"{API_BASE_URL}{endpoint}"
    actor_name = character_details_for_retry["username"] if character_details_for_retry else "SCRIPT"
    if DEBUG_API_CALLS:
        log_sim_action(f"API_CALL ({actor_name})", f"{method} {url}")
        if data: log_sim_action(f"API_DATA ({actor_name})", json.dumps(data))
        if headers:
            safe_headers = {k: (v[:15] + "...'" if k == 'Authorization' and len(v) > 20 else v) for k, v in headers.items()}
            log_sim_action(f"API_HEADERS ({actor_name})", str(safe_headers))
    try:
        response = requests.request(method, url, json=data, headers=headers, timeout=30)
        if DEBUG_API_CALLS:
            log_sim_action(f"API_RESPONSE ({actor_name})", f"Status {response.status_code}")
            if response.content:
                try: log_sim_action(f"API_BODY ({actor_name})", response.json())
                except json.JSONDecodeError: log_sim_action(f"API_BODY_TEXT ({actor_name})", response.text[:100]+"...")
        
        if response.status_code == 401 and headers and 'Authorization' in headers and character_details_for_retry and original_call_args:
            log_sim_action(character_details_for_retry["username"], "Token expired/invalid (401). Attempting re-login.")
            new_original_call_args = original_call_args.copy(); new_original_call_args.pop('character_details_for_retry', None); new_original_call_args.pop('original_call_args', None)
            if login_character_by_details(character_details_for_retry) and registered_characters[character_details_for_retry["username"]].get("token"):
                new_headers = headers.copy(); new_headers['Authorization'] = f"Bearer {registered_characters[character_details_for_retry['username']]['token']}"
                log_sim_action(character_details_for_retry["username"], "Re-login successful. Retrying original API call.")
                return api_call(method, endpoint, data=data, headers=new_headers)
            else: log_sim_action(character_details_for_retry["username"], "Re-login failed. Original action cannot be retried."); return response
        time.sleep(API_DELAY)
        return response
    except requests.exceptions.RequestException as e:
        log_sim_action(actor_name, f"API Call Error for {method} {url}", str(e))
        return None

# Logs in a character using their stored details if their token expired.
def login_character_by_details(char_details):
    if not (char_details and char_details.get("username") and char_details.get("password")):
        log_sim_action("SCRIPT_ERROR", "Cannot re-login: missing username or password in char_details."); return False
    character_name = char_details["username"]
    log_sim_action(character_name, "Attempting re-login")
    login_data = {"username": character_name, "password": char_details["password"]}
    login_response = api_call("POST", "/auth/login", data=login_data)
    if login_response and login_response.status_code == 200:
        token = login_response.json().get("token")
        if token: registered_characters[character_name]["token"] = token; log_sim_action(character_name, "Re-login successful. Token updated."); return True
    log_sim_action(character_name, "Re-login failed.", f"Status: {login_response.status_code if login_response else 'No Response'}"); return False

# Finds character details in my global store by their user_id.
def get_character_details_by_id(user_id):
    for details in registered_characters.values():
        if details.get("user_id") == user_id: return details
    return None

# Registers a character from the play as a user and logs them in.
def register_character(character_name_raw):
    character_name = character_name_raw.strip().upper()
    if not character_name or not re.fullmatch(r"[A-Z\s\'\-\.]+", character_name) or \
       character_name in ["PROLOGUE", "EPILOGUE", "CONTENTS", "ACT", "SCENE", "ALL", "OTHERS", "MUSICK", "SONG"] or \
       len(character_name.split()) > 3 or len(character_name) < 2 :
        return None
    if character_name in registered_characters and registered_characters[character_name].get("token") and registered_characters[character_name].get("user_id"):
        return registered_characters[character_name]

    log_sim_action(character_name, "Attempting registration")
    email_safe_name = re.sub(r'\W+', '', character_name.lower())
    email = f"{email_safe_name}_{uuid.uuid4().hex[:4]}@play-simulation.com"
    password = f"password_{email_safe_name}"
    
    if character_name not in registered_characters:
        registered_characters[character_name] = {"username": character_name, "email": email, "password": password}
    else:
        registered_characters[character_name].setdefault("username", character_name)
        registered_characters[character_name].setdefault("email", email)
        registered_characters[character_name].setdefault("password", password)

    reg_data = {"username": character_name, "email": email, "password": password}
    reg_response = api_call("POST", "/auth/register", data=reg_data)

    if reg_response and reg_response.status_code == 201:
        user_info = reg_response.json().get("user", {}); user_id = user_info.get("user_id")
        log_sim_action(character_name, "Registered successfully", f"ID: {user_id}")
        registered_characters[character_name]["user_id"] = user_id
    elif reg_response and reg_response.status_code == 409:
        log_sim_action(character_name, "Likely already exists (409)", "Attempting login")
    else:
        log_sim_action(character_name, "Registration failed", f"Status: {reg_response.status_code if reg_response else 'No Response'}"); return None
    
    if login_character_by_details(registered_characters[character_name]):
        if not registered_characters[character_name].get("user_id") and registered_characters[character_name].get("token"):
            verify_headers = {"Authorization": f"Bearer {registered_characters[character_name]['token']}"}
            verify_response = api_call("GET", "/auth/verify", headers=verify_headers)
            if verify_response and verify_response.status_code == 200:
                user_id_from_verify = verify_response.json().get("user_id")
                if user_id_from_verify:
                    registered_characters[character_name]["user_id"] = user_id_from_verify
                    log_sim_action(character_name, "User ID confirmed via token verify", f"ID: {user_id_from_verify}")
                else: log_sim_action(character_name, "Verify did not return user_id")
            else: log_sim_action(character_name, "Verify call failed after login")
        
        if registered_characters[character_name].get("user_id"): return registered_characters[character_name]
    log_sim_action(character_name, "Could not establish full user details (ID and Token)."); return None

# Gets an existing 1-on-1 chat or creates a new one.
def get_or_create_1on1_chat(user1_details, user2_details):
    if not all(d and d.get("user_id") and d.get("token") and d.get("username") for d in [user1_details, user2_details]):
        log_sim_action("1ON1_CHAT_CREATION", "Failed: Missing user details for one or both users.")
        return None
    user1_id, user2_id = user1_details["user_id"], user2_details["user_id"]
    user1_name, user2_name = user1_details["username"], user2_details["username"]
    if user1_id == user2_id: return None
    
    chat_pair_key = tuple(sorted((user1_id, user2_id)))
    if chat_pair_key in active_1on1_chats:
        log_sim_action(f"{user1_name}/{user2_name}", f"Using cached 1-on-1 chat", f"ID: {active_1on1_chats[chat_pair_key]['chat_id']}")
        return active_1on1_chats[chat_pair_key]

    log_sim_action(user1_name, f"Checking API for existing 1-on-1 chat with {user2_name}")
    headers1 = {"Authorization": f"Bearer {user1_details['token']}"}
    list_chats_response = api_call("GET", "/chats", headers=headers1, character_details_for_retry=user1_details, original_call_args={"method":"GET", "endpoint":"/chats", "headers": headers1})
    
    if list_chats_response and list_chats_response.status_code == 200:
        existing_chats = list_chats_response.json().get("chats", [])
        for chat in existing_chats:
            if not chat.get("is_group_chat"):
                member_ids_in_chat = {member["user_id"] for member in chat.get("members", [])}
                if member_ids_in_chat == {user1_id, user2_id}:
                    chat_name_from_api = chat.get("chat_name", f"{user1_name} & {user2_name}")
                    chat_info = {"chat_id": chat["chat_id"], "name": chat_name_from_api, "member_ids": list(member_ids_in_chat)}
                    active_1on1_chats[chat_pair_key] = chat_info
                    log_sim_action(user1_name, f"Found existing 1-on-1 chat with {user2_name} via API", f"ID: {chat['chat_id']}")
                    return chat_info
        log_sim_action(user1_name, f"No existing 1-on-1 chat found via API with {user2_name}.")
    else:
        log_sim_action(user1_name, f"Failed to list existing chats for {user1_name} or API error occurred.")

    chat_name_to_create = f"{user1_name} & {user2_name}"
    log_sim_action(user1_name, f"Creating NEW 1-on-1 chat with {user2_name}")
    chat_data = {"participant_ids": [user2_id], "is_group": False}
    chat_response = api_call("POST", "/chats", data=chat_data, headers=headers1, character_details_for_retry=user1_details, original_call_args={"method":"POST", "endpoint":"/chats", "data":chat_data, "headers":headers1})
    if chat_response and chat_response.status_code == 201:
        chat_id = chat_response.json().get("chat", {}).get("chat_id")
        if chat_id:
            chat_info = {"chat_id": chat_id, "name": chat_name_to_create, "member_ids": [user1_id, user2_id]}
            active_1on1_chats[chat_pair_key] = chat_info
            log_sim_action(chat_info["name"], "1-on-1 Chat created successfully", f"ID: {chat_id}")
            return chat_info
    log_sim_action(user1_name, f"Failed to create 1-on-1 chat with {user2_name}")
    return None

# Creates a group chat for a scene.
def create_group_chat(creator_details, participant_details_list, scene_key):
    if not creator_details or not creator_details.get("user_id") or not creator_details.get("token"):
        log_sim_action("GROUP_CHAT_CREATION", "Failed: Missing creator details/ID/token"); return None
    participant_ids = [p["user_id"] for p in participant_details_list if p and p.get("user_id") and p["user_id"] != creator_details["user_id"]]
    if not participant_ids:
        log_sim_action(creator_details["username"], f"Failed to create group for scene '{scene_key}': No other valid participants found.")
        return None
    actual_group_name = scene_key.replace("_", " ") + " Group"
    log_sim_action(creator_details["username"], f"Creating group chat '{actual_group_name}' for scene '{scene_key}'")
    chat_data = {"participant_ids": participant_ids, "is_group": True, "chat_name": actual_group_name}
    headers = {"Authorization": f"Bearer {creator_details['token']}"}
    chat_response = api_call("POST", "/chats", data=chat_data, headers=headers, character_details_for_retry=creator_details, original_call_args={"method":"POST", "endpoint":"/chats", "data":chat_data, "headers":headers})
    if chat_response and chat_response.status_code == 201:
        chat_id = chat_response.json().get("chat", {}).get("chat_id")
        if chat_id:
            all_member_ids = [creator_details["user_id"]] + participant_ids
            chat_info = {"chat_id": chat_id, "name": actual_group_name, "member_ids": sorted(list(set(all_member_ids)))}
            active_group_chats[scene_key] = chat_info
            log_sim_action(actual_group_name, "Group chat created successfully", f"ID: {chat_id}")
            return chat_info
    log_sim_action(creator_details["username"], f"Failed to create group chat '{actual_group_name}' for scene '{scene_key}'")
    return None

# Simulates another user in the chat reading recent messages.
def simulate_immediate_read(chat_id, chat_name, members_in_chat_ids, sender_id):
    if not SIMULATE_READING_AFTER_SEND or not members_in_chat_ids: return
    other_members = [uid for uid in members_in_chat_ids if uid != sender_id]
    if not other_members: return
    reader_id = random.choice(other_members)
    reader_details = get_character_details_by_id(reader_id)
    if reader_details and reader_details.get("token"):
        log_sim_action(reader_details["username"], f"Simulating IMMEDIATE read from chat '{chat_name}' (ID: {chat_id})")
        headers = {"Authorization": f"Bearer {reader_details['token']}"}
        api_call("GET", f"/chats/{chat_id}/messages?limit=5", headers=headers, character_details_for_retry=reader_details, original_call_args={"method":"GET", "endpoint":f"/chats/{chat_id}/messages?limit=5", "headers":headers})
        time.sleep(DELAY_BETWEEN_READ_ACTIONS / 2)
    else: log_sim_action("SCRIPT_ERROR", f"Could not find token for reader ID {reader_id} for immediate read in chat {chat_id}")

# Sends a message to a specified chat and simulates an immediate read.
def send_message_to_chat(chat_id, chat_name, sender_details, content, members_in_chat_ids):
    if not content or not sender_details or not sender_details.get("token") or not sender_details.get("username") or not chat_id:
        log_sim_action("MESSAGE_SENDING", "Failed: Missing critical info (content, sender details, token, username, or chat_id)")
        return False
    log_sim_action(sender_details["username"], f"Sending message to Chat '{chat_name}' (ID: {chat_id})", f"'{content[:30]}...'")
    message_data = {"content": content.strip()}
    headers = {"Authorization": f"Bearer {sender_details['token']}"}
    response = api_call("POST", f"/chats/{chat_id}/messages", data=message_data, headers=headers, character_details_for_retry=sender_details, original_call_args={"method":"POST", "endpoint":f"/chats/{chat_id}/messages", "data":message_data, "headers":headers})
    success = response and response.status_code == 201
    if not success:
        log_sim_action(sender_details["username"], f"Failed to send message to Chat '{chat_name}' (ID: {chat_id})")
    else:
        simulate_immediate_read(chat_id, chat_name, members_in_chat_ids, sender_details["user_id"])
    return success

# Parses the "Dramatis Personae" to identify and register main characters.
def parse_dramatis_personae(lines):
    log_sim_action("SCRIPT", "Parsing Dramatis Personae")
    in_dramatis_section = False; character_names = []
    char_regex = re.compile(r"^([A-Z][A-Z\s\-\'\.]{1,})(?:,|\s\(|\s\–|\s—|$)")
    excluded_titles_etc = ["SCENE", "CONTENTS", "ACT", "THE LATE", "DANISH CAPTAIN", "ENGLISH", "LORDS", "LADIES", "OFFICERS", "SOLDIERS", "SAILORS", "MESSENGERS", "ATTENDANTS", "PLAYERS", "TWO", "A", "GHOST", "PROLOGUE", "EPILOGUE", "ALL", "OTHERS", "HIS", "HER", "SON", "DAUGHTER", "WIFE", "FRIEND", "SERVANT", "TO"]
    for line_num, line_content in enumerate(lines):
        line_strip = line_content.strip()
        if "Dramatis Personæ" in line_strip or "Characters in the Play" in line_strip or "PERSONS REPRESENTED" in line_strip:
            in_dramatis_section = True; log_sim_action("SCRIPT", f"Dramatis Personae section started at line {line_num + 1}"); continue
        if in_dramatis_section:
            if any(marker in line_strip for marker in ["SCENE.", "ACT I", "PROLOGUE", "*** START OF THIS PROJECT GUTENBERG EBOOK", "THE SCENE"]):
                if line_strip.startswith(("SCENE.", "ACT I", "PROLOGUE", "THE SCENE")): log_sim_action("SCRIPT", f"Dramatis Personae section ended at line {line_num + 1} due to marker: {line_strip}"); break
            if not line_strip and line_num + 1 < len(lines):
                 if any(marker in lines[line_num+1] for marker in ["SCENE.", "ACT I", "PROLOGUE"]): log_sim_action("SCRIPT", f"Dramatis Personae section ended at line {line_num + 1} (blank) due to upcoming marker."); break
            if not char_regex.match(line_strip) and len(line_strip) > 0 and not line_strip[0].islower():
                if len(character_names) > 3: log_sim_action("SCRIPT", f"Dramatis Personae section likely ended at line {line_num + 1} (format change): {line_strip}"); break
            match = char_regex.match(line_strip)
            if match:
                name = match.group(1).strip().upper()
                for title in excluded_titles_etc + ["KING", "QUEEN", "PRINCE", "PRINCESS", "DUKE", "DUCHESS", "LORD", "LADY", "SIR", "MISTRESS", "MASTER", "FAIRY"]:
                    name = re.sub(r'\b' + re.escape(title) + r'\b', '', name, flags=re.IGNORECASE).strip()
                name = re.sub(r'\s*OF\s*[A-Z\s]+$', '', name, flags=re.IGNORECASE).strip()
                name = re.sub(r'[,\.]+$', '', name).strip(); name = ' '.join(name.split());
                if name and name not in excluded_titles_etc and len(name) > 1 and not name.isdigit() and " AND " not in name:
                    character_names.append(name) # Store as initially parsed (upper)
    unique_names = sorted(list(set(character_names)))
    log_sim_action("SCRIPT", f"Found characters in Dramatis Personae: {unique_names}")
    for name in unique_names: register_character(name) # register_character will .upper() it
    log_sim_action("SCRIPT", "Finished pre-registering characters from Dramatis Personae.")

# Processes the entire play text line by line.
def process_play_text(file_path):
    log_sim_action("SCRIPT", f"Starting to process play text: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
        log_sim_action("SCRIPT", f"Successfully read {len(lines)} lines from {file_path}")
    except FileNotFoundError: log_sim_action("SCRIPT", f"Error: File not found at {file_path}"); return
    except Exception as e: log_sim_action("SCRIPT", f"Error reading file {file_path}: {e}"); return

    dramatis_personae_end_index = 0; found_dramatis_start = False
    for i, line in enumerate(lines):
        if "Dramatis Personæ" in line or "Characters in the Play" in line or "PERSONS REPRESENTED" in line:
            found_dramatis_start = True
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith(("ACT I", "SCENE I.", "PROLOGUE", "THE SCENE")) or "*** START OF THIS PROJECT GUTENBERG EBOOK" in lines[j] or \
                   (lines[j].strip() == "" and j + 1 < len(lines) and (lines[j+1].strip().startswith(("ACT I", "SCENE I.")))):
                    dramatis_personae_end_index = j; break
            else: dramatis_personae_end_index = i + 40 
            if dramatis_personae_end_index > i: parse_dramatis_personae(lines[i:dramatis_personae_end_index])
            break
    if not found_dramatis_start: log_sim_action("SCRIPT", "Dramatis Personae section not found or not clearly identified.")

    character_line_regex = re.compile(r"^\s*([A-Z][A-Za-z\s\-\'\.]{1,})\.\s*$") 
    stage_direction_regex = re.compile(r"^\s*\[.*?\]\s*$")
    scene_act_regex = re.compile(r"^\s*(ACT\s+[IVXLCDM]+|SCENE\s+[IVXLCDM]+|PROLOGUE|EPILOGUE)\b", re.IGNORECASE)

    current_speaker_details = None; previous_speaker_details = None
    current_dialogue_lines = []; current_1on1_chat_info = None
    current_scene_group_chat_info = None; current_scene_speakers_details = []
    current_scene_key = "default_scene"

    start_line_index = dramatis_personae_end_index
    if start_line_index == 0:
        for i, line in enumerate(lines):
            if line.strip().startswith(("ACT I", "SCENE I.")): start_line_index = i; break
    log_sim_action("SCRIPT", f"Starting main dialogue parsing from line {start_line_index}")

    # This loop identifies speakers and their dialogue.
    for i in range(start_line_index, len(lines)):
        line = lines[i]; stripped_line = line.strip()
        if not stripped_line: continue

        # Handles scene changes and sets up scene context.
        if scene_act_regex.match(stripped_line):
            log_sim_action("SCENE_CHANGE", stripped_line)
            if current_speaker_details and current_dialogue_lines:
                if current_1on1_chat_info: send_message_to_chat(current_1on1_chat_info["chat_id"], current_1on1_chat_info["name"], current_speaker_details, " ".join(current_dialogue_lines), current_1on1_chat_info["member_ids"])
                if current_scene_group_chat_info: send_message_to_chat(current_scene_group_chat_info["chat_id"], current_scene_group_chat_info["name"], current_speaker_details, " ".join(current_dialogue_lines), current_scene_group_chat_info["member_ids"])
            current_scene_key = stripped_line.replace(" ", "_").replace(".","").upper()
            current_scene_speakers_details = []
            current_scene_group_chat_info = active_group_chats.get(current_scene_key)
            if current_scene_group_chat_info:
                 log_sim_action("SCRIPT", f"Rejoining existing group chat for scene '{current_scene_group_chat_info['name']}' (ID: {current_scene_group_chat_info['chat_id']})")
            else:
                 log_sim_action("SCRIPT", f"New scene '{current_scene_key}', group chat to be formed.")
            current_dialogue_lines = []; previous_speaker_details = None; current_speaker_details = None; current_1on1_chat_info = None
            continue

        # Handles stage directions, sending pending dialogue.
        if stage_direction_regex.match(stripped_line):
            if current_speaker_details and current_dialogue_lines:
                if current_1on1_chat_info: send_message_to_chat(current_1on1_chat_info["chat_id"], current_1on1_chat_info["name"], current_speaker_details, " ".join(current_dialogue_lines), current_1on1_chat_info["member_ids"])
                if current_scene_group_chat_info: send_message_to_chat(current_scene_group_chat_info["chat_id"], current_scene_group_chat_info["name"], current_speaker_details, " ".join(current_dialogue_lines), current_scene_group_chat_info["member_ids"])
            current_dialogue_lines = []
            if "[_Exit" in stripped_line or "[_Exeunt" in stripped_line: current_speaker_details = None
            continue

        char_match = character_line_regex.match(stripped_line)
        # This block processes a line identified as a speaker.
        if char_match:
            new_speaker_name_raw = char_match.group(1).strip().upper()
            new_speaker_details = registered_characters.get(new_speaker_name_raw)
            if not new_speaker_details:
                if len(new_speaker_name_raw) > 1 and (new_speaker_name_raw.isupper() or len(new_speaker_name_raw.split()) > 1 or new_speaker_name_raw in ["PUCK"]) and \
                   new_speaker_name_raw not in ["ACT", "SCENE", "PROLOGUE", "EPILOGUE"] and \
                   not any(kw in new_speaker_name_raw for kw in ["AMBASSADORS", "ATTENDANTS", "LORDS", "LADIES"]):
                    new_speaker_details = register_character(new_speaker_name_raw)
                if not new_speaker_details:
                    if current_speaker_details: current_dialogue_lines.append(stripped_line)
                    continue
            
            if new_speaker_details.get("user_id") and new_speaker_details not in current_scene_speakers_details:
                 current_scene_speakers_details.append(new_speaker_details)

            if len(current_scene_speakers_details) >= 2 and not current_scene_group_chat_info:
                if not active_group_chats.get(current_scene_key):
                    creator_for_group = current_scene_speakers_details[0]
                    other_participants_for_group = [spd for spd in current_scene_speakers_details if spd.get("user_id") != creator_for_group.get("user_id")]
                    if other_participants_for_group: 
                         current_scene_group_chat_info = create_group_chat(creator_for_group, other_participants_for_group, current_scene_key)
                else: current_scene_group_chat_info = active_group_chats[current_scene_key]

            if current_speaker_details and current_speaker_details.get("user_id") != new_speaker_details.get("user_id"):
                if current_dialogue_lines:
                    if current_1on1_chat_info: send_message_to_chat(current_1on1_chat_info["chat_id"], current_1on1_chat_info["name"], current_speaker_details, " ".join(current_dialogue_lines), current_1on1_chat_info["member_ids"])
                    if current_scene_group_chat_info: send_message_to_chat(current_scene_group_chat_info["chat_id"], current_scene_group_chat_info["name"], current_speaker_details, " ".join(current_dialogue_lines), current_scene_group_chat_info["member_ids"])
                current_dialogue_lines = []
                previous_speaker_details = current_speaker_details
            current_speaker_details = new_speaker_details
            if previous_speaker_details and current_speaker_details.get("user_id") != previous_speaker_details.get("user_id"):
                current_1on1_chat_info = get_or_create_1on1_chat(previous_speaker_details, current_speaker_details)
            elif not previous_speaker_details and current_speaker_details:
                 previous_speaker_details = current_speaker_details; current_1on1_chat_info = None
        # This block collects dialogue lines for the current speaker.
        elif current_speaker_details:
            dialogue_part = line.strip()
            if dialogue_part: current_dialogue_lines.append(dialogue_part)

    # Sends any final dialogue after processing all lines.
    if current_speaker_details and current_dialogue_lines:
        if current_1on1_chat_info: send_message_to_chat(current_1on1_chat_info["chat_id"], current_1on1_chat_info["name"], current_speaker_details, " ".join(current_dialogue_lines), current_1on1_chat_info["member_ids"])
        if current_scene_group_chat_info: send_message_to_chat(current_scene_group_chat_info["chat_id"], current_scene_group_chat_info["name"], current_speaker_details, " ".join(current_dialogue_lines), current_scene_group_chat_info["member_ids"])
    log_sim_action("SCRIPT", "Finished processing play text.")

# Simulates users reading historical messages from chats.
def simulate_historical_message_reading():
    if not SIMULATE_HISTORICAL_READING_END: return
    log_sim_action("SCRIPT", "Starting HISTORICAL message reading simulation phase...")
    all_simulated_chats_info = list(active_1on1_chats.values()) + list(active_group_chats.values())
    if not all_simulated_chats_info: log_sim_action("SCRIPT", "No active chats to simulate historical reading for."); return

    for chat_info in all_simulated_chats_info:
        chat_id, chat_name, member_ids = chat_info["chat_id"], chat_info["name"], chat_info.get("member_ids", [])
        if not member_ids: continue
        reader_id = random.choice(member_ids)
        reader_details = get_character_details_by_id(reader_id)
        if reader_details and reader_details.get("token"):
            num_historical_fetches = random.randint(1, MAX_HISTORICAL_READS_PER_CHAT)
            log_sim_action(reader_details["username"], f"Will attempt {num_historical_fetches} historical reads for chat '{chat_name}' (ID: {chat_id})")
            headers = {"Authorization": f"Bearer {reader_details['token']}"}
            oldest_ts_in_batch = None
            response_recent = api_call("GET", f"/chats/{chat_id}/messages?limit=10", headers=headers, character_details_for_retry=reader_details, original_call_args={"method":"GET", "endpoint":f"/chats/{chat_id}/messages?limit=10", "headers":headers})
            if response_recent and response_recent.status_code == 200:
                messages = response_recent.json().get("messages", [])
                if messages: oldest_ts_in_batch = messages[-1].get("created_at")
            if not oldest_ts_in_batch: log_sim_action(reader_details["username"], f"No recent messages found for chat '{chat_name}'. Skipping historical reads for this chat."); continue
            for i in range(num_historical_fetches):
                log_sim_action(reader_details["username"], f"Reading historical page {i+1}/{num_historical_fetches} for chat '{chat_name}' before {oldest_ts_in_batch}")
                response_hist = api_call("GET", f"/chats/{chat_id}/messages?before_timestamp={oldest_ts_in_batch}&limit=5", headers=headers, character_details_for_retry=reader_details, original_call_args={"method":"GET", "endpoint":f"/chats/{chat_id}/messages?before_timestamp={oldest_ts_in_batch}&limit=5", "headers":headers})
                if response_hist and response_hist.status_code == 200:
                    hist_messages = response_hist.json().get("messages", [])
                    if hist_messages: oldest_ts_in_batch = hist_messages[-1].get("created_at")
                    else: log_sim_action(reader_details["username"], f"No more historical messages for chat '{chat_name}'."); break
                else: log_sim_action(reader_details["username"], f"Failed to fetch historical page {i+1} for chat '{chat_name}'."); break
                time.sleep(DELAY_BETWEEN_READ_ACTIONS)
        else: log_sim_action("SCRIPT_ERROR", f"Could not find token for reader ID {reader_id} for historical read in chat {chat_id}")

# Main entry point for the script.
if __name__ == "__main__":
    log_sim_action("SCRIPT", "--- SCRIPT START ---")
    print("Ensure your Flask backend API (http://localhost:5000) is running in Docker.")
    start_script = input("Press Enter to start the Play Simulator (or 'q' to quit)...")
    if start_script.lower() == 'q': log_sim_action("SCRIPT", "Exiting script."); exit()

    log_sim_action("SCRIPT", "--- STARTING PLAY PROCESSING ---")
    process_play_text(TEXT_FILE_PATH)
    if SIMULATE_HISTORICAL_READING_END: simulate_historical_message_reading()

    log_sim_action("SCRIPT","--- FINAL SIMULATION SUMMARY ---")
    log_sim_action("SCRIPT", f"Total characters registered: {len(registered_characters)}")
    printable_1on1_chats_summary = {}
    for key_tuple, chat_data_val in active_1on1_chats.items():
        user1_id, user2_id = key_tuple
        user1_name = get_character_details_by_id(user1_id).get("username", str(user1_id)) if get_character_details_by_id(user1_id) else str(user1_id)
        user2_name = get_character_details_by_id(user2_id).get("username", str(user2_id)) if get_character_details_by_id(user2_id) else str(user2_id)
        printable_1on1_chats_summary[f"Chat between {user1_name} & {user2_name}"] = {"chat_id": chat_data_val["chat_id"], "members": chat_data_val["member_ids"]}
    log_sim_action("SCRIPT", f"Total 1-on-1 chats created/used: {len(printable_1on1_chats_summary)}")
    if DEBUG_API_CALLS or VERBOSE_SIMULATION_LOGS:
        for name, data in printable_1on1_chats_summary.items():
            log_sim_action("1-ON-1 CHAT", name, f"ID: {data['chat_id']}, Members: {data['members']}")
    log_sim_action("SCRIPT", f"Total group chats created: {len(active_group_chats)}")
    if DEBUG_API_CALLS or VERBOSE_SIMULATION_LOGS:
        for name, data in active_group_chats.items():
            log_sim_action("GROUP CHAT", data["name"], f"ID: {data['chat_id']}, Members: {data['member_ids']}")
    print("\nScript finished. Check API logs, RedisInsight, and MySQL Workbench for results.")

