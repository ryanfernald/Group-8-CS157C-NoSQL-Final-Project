# File: your_chat_project/app/models/chat.py

from app import db
from datetime import datetime

class Chat(db.Model):
    __tablename__ = 'chats'

    chat_id = db.Column(db.Integer, primary_key=True)
    is_group_chat = db.Column(db.Boolean, default=False, nullable=False)
    chat_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    # Removed lazy='dynamic' from the 'members' collection
    members = db.relationship('ChatMember', back_populates='chat', cascade="all, delete-orphan")
    # Removed lazy='dynamic' from the 'messages' collection (good practice if you might eager load it later)
    messages = db.relationship('Message', back_populates='chat', cascade="all, delete-orphan")

    def __repr__(self):
        name = self.chat_name if self.is_group_chat and self.chat_name else f"Chat {self.chat_id}"
        return f'<Chat {name}>'
