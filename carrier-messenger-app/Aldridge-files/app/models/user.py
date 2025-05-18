from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Defines the User model with authentication and relationship helpers
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    memberships = db.relationship('ChatMember', back_populates='user', cascade="all, delete-orphan")
    messages_sent = db.relationship('Message', back_populates='sender')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() + 'Z'
        }

    def __repr__(self):
        return f'<User {self.username}>'
