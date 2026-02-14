from __future__ import annotations
from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(32))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="ADMIN")  # ADMIN, MANAGER, HOST, CASHIER
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # flask-login compatibility
    def get_id(self):
        return str(self.id)

class Reservation(db.Model):
    __tablename__ = "reservations"
    id = db.Column(db.Integer, primary_key=True)
    ticket_code = db.Column(db.String(12), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(32))
    guests = db.Column(db.Integer, nullable=False, default=2)
    reserve_date = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD
    reserve_time = db.Column(db.String(10), nullable=False)  # HH:MM
    status = db.Column(db.String(20), nullable=False, default="WAITING")  # WAITING, READY, SEATED, DONE, CANCELLED
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
