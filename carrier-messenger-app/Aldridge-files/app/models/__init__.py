# File: your_chat_project/app/models/__init__.py

# Import models to make them accessible when 'app.models' is imported
from .user import User
from .chat import Chat
from .chat_member import ChatMember
from .message import Message

# You can optionally define __all__ to control what `from . import *` does
__all__ = ['User', 'Chat', 'ChatMember', 'Message']
