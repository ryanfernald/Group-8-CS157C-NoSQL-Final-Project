# File: your_chat_project/app/services/chat_service.py

from app import db
from app.models import User, Chat, ChatMember
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from sqlalchemy.exc import IntegrityError

def create_chat(creator_user: User, participant_ids: list[int], is_group: bool, chat_name: str = None):
    """
    Creates a new chat (one-on-one or group) and adds participants.

    Args:
        creator_user: The User object of the person initiating the chat.
        participant_ids: A list of user_ids to include in the chat (excluding the creator).
        is_group: Boolean indicating if it's a group chat.
        chat_name: Optional name for the chat (required for group chats).

    Returns:
        The newly created Chat object.

    Raises:
        BadRequest: If input is invalid (e.g., no participants, missing name for group chat).
        NotFound: If any participant ID doesn't correspond to an existing user.
        Forbidden: If trying to create a 1-on-1 chat with self or more than one other participant.
        IntegrityError: If there's a database constraint issue (should be rare with checks).
    """
    print(f"SERVICE: Attempting to create chat. Creator: {creator_user.user_id}, Participants: {participant_ids}, Group: {is_group}, Name: {chat_name}")

    # --- Input Validation ---
    if not participant_ids:
        raise BadRequest("At least one participant ID must be provided.")

    if is_group and not chat_name:
        raise BadRequest("Group chats must have a name.")

    # Combine creator and participant IDs, ensuring uniqueness
    all_member_ids = set([creator_user.user_id] + participant_ids)

    if not is_group:
        if len(all_member_ids) != 2:
             raise BadRequest("One-on-one chats must have exactly two distinct participants (creator + one other).")
        if creator_user.user_id in participant_ids:
             raise BadRequest("Cannot create a one-on-one chat with yourself.")

    # --- Check if Participants Exist ---
    # Fetch all potential members from the database in one query
    members = User.query.filter(User.user_id.in_(all_member_ids)).all()
    if len(members) != len(all_member_ids):
        found_ids = {user.user_id for user in members}
        missing_ids = all_member_ids - found_ids
        raise NotFound(f"Users not found: {list(missing_ids)}")

    # --- Create Chat and Add Members (Transaction) ---
    try:
        # Create the chat entry
        new_chat = Chat(
            is_group_chat=is_group,
            chat_name=chat_name if is_group else None
        )
        db.session.add(new_chat)
        # We need the chat_id, so flush to get it assigned by the DB
        db.session.flush()
        print(f"SERVICE: Flushed chat, got ID: {new_chat.chat_id}")

        # Create ChatMember entries for all participants (including creator)
        for user in members:
            member_entry = ChatMember(user_id=user.user_id, chat_id=new_chat.chat_id)
            db.session.add(member_entry)

        # Commit the transaction
        db.session.commit()
        print(f"SERVICE: Chat {new_chat.chat_id} created successfully with members: {all_member_ids}")
        return new_chat

    except IntegrityError as e:
        db.session.rollback()
        print(f"ERROR: Database integrity error during chat creation: {e}")
        # This might happen if a unique constraint fails unexpectedly
        raise BadRequest("Could not create chat due to a data conflict.")
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Unexpected error during chat creation: {e}")
        raise # Re-raise other unexpected errors

# Add other chat-related service functions here later (e.g., get_user_chats)

