"""
User Model — Auth + Subscription + API Keys
"""

import uuid
import hashlib
import secrets
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)

    # Auth
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), nullable=True)
    password_reset_token = db.Column(db.String(100), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)

    # OAuth
    oauth_provider = db.Column(db.String(50), nullable=True)
    oauth_id = db.Column(db.String(200), nullable=True)

    # Subscription
    plan = db.Column(db.String(50), default="free")
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    subscription_status = db.Column(db.String(50), default="inactive")
    subscription_ends_at = db.Column(db.DateTime, nullable=True)
    trial_ends_at = db.Column(db.DateTime, nullable=True)

    # API
    api_key = db.Column(db.String(64), unique=True, nullable=True)
    api_calls_count = db.Column(db.Integer, default=0)
    api_calls_reset_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    api_keys = db.relationship("APIKey", backref="user", lazy="dynamic", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_api_key(self) -> str:
        key = secrets.token_urlsafe(32)
        self.api_key = key
        return key

    def generate_email_token(self) -> str:
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        return token

    def generate_password_reset_token(self) -> str:
        from datetime import timedelta
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=2)
        return token

    @property
    def is_subscribed(self) -> bool:
        return self.subscription_status == "active"

    @property
    def is_on_trial(self) -> bool:
        if self.trial_ends_at:
            return datetime.utcnow() < self.trial_ends_at
        return False

    @property
    def gravatar_url(self) -> str:
        email_hash = hashlib.md5(self.email.lower().encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=80"

    def to_dict(self) -> dict:
        return {
            "id": self.uuid,
            "email": self.email,
            "name": self.name,
            "plan": self.plan,
            "subscription_status": self.subscription_status,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<User {self.email}>"


class APIKey(db.Model):
    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False, default="Default")
    is_active = db.Column(db.Boolean, default=True)
    last_used_at = db.Column(db.DateTime, nullable=True)
    calls_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def generate(cls, user_id: int, name: str = "Default") -> "APIKey":
        key = APIKey(
            user_id=user_id,
            key=secrets.token_urlsafe(32),
            name=name
        )
        return key


@login_manager.user_loader
def load_user(user_id: int) -> User:
    return User.query.get(int(user_id))
