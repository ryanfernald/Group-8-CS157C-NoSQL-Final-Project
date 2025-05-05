# File: your_chat_project/app/models/user.py

from app import db # Import the db instance from the app package
from datetime import datetime
# Import password hashing utilities later if needed
# from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users' # Explicitly naming the table

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False) # Store hash, not password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (optional but helpful for ORM usage)
    # 'ChatMember' links User to Chat
    memberships = db.relationship('ChatMember', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")
    # Messages sent by this user
    messages_sent = db.relationship('Message', back_populates='sender', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    # Add methods for password hashing and verification here later
    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     return check_password_hash(self.password_hash, password)
