# File: your_chat_project/app/models/message.py

from app import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(db.BigInteger, primary_key=True) # Using BigInteger for potentially many messages
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.chat_id'), nullable=False, index=True) # Index chat_id
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False) # Use Text for potentially long messages
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True) # Index timestamp

    # Define relationships to User (sender) and Chat
    sender = db.relationship('User', back_populates='messages_sent')
    chat = db.relationship('Chat', back_populates='messages')

    # Add index for efficient querying of messages within a chat ordered by time
    __table_args__ = (db.Index('ix_messages_chat_id_created_at', 'chat_id', 'created_at'),)

    def __repr__(self):
        return f'<Message {self.message_id} from User:{self.sender_id} in Chat:{self.chat_id}>'

