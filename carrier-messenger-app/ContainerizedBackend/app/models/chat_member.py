from app import db
from datetime import datetime

# Defines the association model representing a user's membership in a chat
class ChatMember(db.Model):
    __tablename__ = 'chat_members'

    membership_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.chat_id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_read_timestamp = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', back_populates='memberships')
    chat = db.relationship('Chat', back_populates='members')

    __table_args__ = (db.UniqueConstraint('user_id', 'chat_id', name='_user_chat_uc'),)

    def __repr__(self):
        return f'<ChatMember User:{self.user_id} Chat:{self.chat_id}>'
