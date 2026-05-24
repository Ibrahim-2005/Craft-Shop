from datetime import datetime, timedelta
import secrets

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=True, index=True)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(40))
    password_hash = db.Column(db.String(255), nullable=False)
    reset_token_hash = db.Column(db.String(255))
    reset_token_expires_at = db.Column(db.DateTime)
    is_active_account = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return f"customer:{self.id}"

    @property
    def display_name(self):
        return self.username or self.name

    @property
    def role_type(self):
        return "customer"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        token = secrets.token_urlsafe(32)
        self.reset_token_hash = generate_password_hash(token)
        self.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        return token

    def check_reset_token(self, token):
        if not self.reset_token_hash or not self.reset_token_expires_at:
            return False
        if self.reset_token_expires_at < datetime.utcnow():
            return False
        return check_password_hash(self.reset_token_hash, token)

    def clear_reset_token(self):
        self.reset_token_hash = None
        self.reset_token_expires_at = None
