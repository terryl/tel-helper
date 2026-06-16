from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(100))
    session_name = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('Message', backref='account', lazy='dynamic')
    replies = db.relationship('AutoReply', backref='account', lazy='dynamic')

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')
    status = db.Column(db.String(20), default='pending')
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AutoReply(db.Model):
    __tablename__ = 'auto_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    keyword = db.Column(db.String(200), nullable=False)
    reply_text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScannedMember(db.Model):
    __tablename__ = 'scanned_members'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(100), nullable=False)
    group_name = db.Column(db.String(200))
    user_id = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)
