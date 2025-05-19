from app import db
from app.models import User, Chat, ChatMember
from werkzeug.exceptions import BadRequest, NotFound, Forbidden, InternalServerError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

# Creates a new chat (group or one-on-one) and adds all specified participants
def create_chat(creator_user: User, participant_ids: list[int], is_group: bool, chat_name: str = None):
    print(f"SERVICE: Attempting to create chat. Creator: {creator_user.user_id}, Participants: {participant_ids}, Group: {is_group}, Name: {chat_name}")
    if not participant_ids: raise BadRequest("At least one participant ID must be provided.")
    if is_group and not chat_name: raise BadRequest("Group chats must have a name.")
    all_member_ids = set([creator_user.user_id] + participant_ids)
    if not is_group:
        if len(all_member_ids) != 2: raise BadRequest("One-on-one chats must have exactly two distinct participants (creator + one other).")
        if creator_user.user_id in participant_ids: raise BadRequest("Cannot create a one-on-one chat with yourself.")
    members = User.query.filter(User.user_id.in_(all_member_ids)).all()
    if len(members) != len(all_member_ids):
        found_ids = {user.user_id for user in members}
        missing_ids = all_member_ids - found_ids
        raise NotFound(f"Users not found: {list(missing_ids)}")
    try:
        new_chat = Chat(is_group_chat=is_group, chat_name=chat_name if is_group else None)
        db.session.add(new_chat)
        db.session.flush()
        print(f"SERVICE: Flushed chat, got ID: {new_chat.chat_id}")
        for user in members:
            member_entry = ChatMember(user_id=user.user_id, chat_id=new_chat.chat_id)
            db.session.add(member_entry)
        db.session.commit()
        print(f"SERVICE: Chat {new_chat.chat_id} created successfully with members: {all_member_ids}")
        return new_chat
    except IntegrityError as e:
        db.session.rollback()
        print(f"ERROR: Database integrity error during chat creation: {e}")
        raise BadRequest("Could not create chat due to a data conflict.")
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Unexpected error during chat creation: {e}")
        raise InternalServerError("An unexpected error occurred during chat creation.")

# Retrieves all chats the user is a member of, using eager loading for performance
def get_user_chats(user: User):
    print(f"SERVICE: Attempting to get chats for User ID {user.user_id}")
    try:
        memberships = ChatMember.query.filter_by(user_id=user.user_id)\
            .options(
                joinedload(ChatMember.chat).options(
                    selectinload(Chat.members).options(
                        joinedload(ChatMember.user, innerjoin=True)
                    )
                )
            ).all()

        chat_list = []
        processed_chat_ids = set()

        for membership in memberships:
            chat = membership.chat
            if chat.chat_id in processed_chat_ids:
                continue
            processed_chat_ids.add(chat.chat_id)

            chat_data = {
                "chat_id": chat.chat_id,
                "is_group_chat": chat.is_group_chat,
                "chat_name": chat.chat_name,
                "members": [],
            }

            other_members = []
            if chat.members:
                for member_obj in chat.members:
                    if member_obj.user:
                        member_user = member_obj.user
                        member_data = {
                            "user_id": member_user.user_id,
                            "username": member_user.username
                        }
                        chat_data["members"].append(member_data)
                        if not chat.is_group_chat and member_user.user_id != user.user_id:
                            other_members.append(member_data)
                    else:
                        print(f"WARNING: User not loaded for member {member_obj.membership_id} in chat {chat.chat_id}")

            if not chat.is_group_chat:
                if other_members:
                    chat_data["chat_name"] = other_members[0]["username"]
                else:
                    print(f"WARNING: Could not determine other member for 1-on-1 chat {chat.chat_id}")
                    chat_data["chat_name"] = "Direct Chat"

            chat_list.append(chat_data)

        print(f"SERVICE: Found {len(chat_list)} chats for User ID {user.user_id}")
        return chat_list

    except Exception as e:
        print(f"ERROR: Unexpected error during get_user_chats for User ID {user.user_id}: {e}")
        raise InternalServerError("An error occurred while retrieving chats.")
