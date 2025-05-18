from app import db
from datetime import datetime

# Defines the Message model representing a single message in a chat
class Message(db.Model):
    __tablename__ = 'messages'

    message_id = db.Column(db.BigInteger, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.chat_id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    sender = db.relationship('User', back_populates='messages_sent')
    chat = db.relationship('Chat', back_populates='messages')

    __table_args__ = (db.Index('ix_messages_chat_id_created_at', 'chat_id', 'created_at'),)

    def __repr__(self):
        return f'<Message {self.message_id} from User:{self.sender_id} in Chat:{self.chat_id}>'
