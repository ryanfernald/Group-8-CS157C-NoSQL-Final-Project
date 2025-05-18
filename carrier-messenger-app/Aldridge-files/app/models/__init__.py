# Makes all model classes directly accessible via 'app.models'
from .user import User
from .chat import Chat
from .chat_member import ChatMember
from .message import Message

__all__ = ['User', 'Chat', 'ChatMember', 'Message']
