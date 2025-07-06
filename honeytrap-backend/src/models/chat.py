from src.models.user import db
from datetime import datetime
import json

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    user_ip = db.Column(db.String(45), nullable=False)  # IPv6 compatible
    user_agent = db.Column(db.Text, nullable=True)
    geolocation = db.Column(db.Text, nullable=True)  # JSON string
    vpn_detected = db.Column(db.Boolean, default=False)
    escalation_level = db.Column(db.Integer, default=0)  # 0=normal, 1=suspicious, 2=high_risk
    evidence_captured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    evidence = db.relationship('Evidence', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'persona_id': self.persona_id,
            'user_ip': self.user_ip,
            'user_agent': self.user_agent,
            'geolocation': json.loads(self.geolocation) if self.geolocation else None,
            'vpn_detected': self.vpn_detected,
            'escalation_level': self.escalation_level,
            'evidence_captured': self.evidence_captured,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    sender_type = db.Column(db.String(10), nullable=False)  # 'user' or 'decoy'
    message_content = db.Column(db.Text, nullable=False)
    sentiment_score = db.Column(db.Float, nullable=True)
    threat_level = db.Column(db.Integer, default=0)  # 0=safe, 1=concerning, 2=threatening
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender_type': self.sender_type,
            'message_content': self.message_content,
            'sentiment_score': self.sentiment_score,
            'threat_level': self.threat_level,
            'timestamp': self.timestamp.isoformat()
        }

class Persona(db.Model):
    __tablename__ = 'personas'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    platform_type = db.Column(db.String(50), nullable=False)  # 'tiktok', 'discord', 'snapchat'
    personality_traits = db.Column(db.Text, nullable=False)  # JSON string
    language_style = db.Column(db.Text, nullable=False)  # JSON string with slang, phrases
    response_patterns = db.Column(db.Text, nullable=False)  # JSON string
    avatar_url = db.Column(db.String(255), nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('ChatSession', backref='persona', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'platform_type': self.platform_type,
            'personality_traits': json.loads(self.personality_traits),
            'language_style': json.loads(self.language_style),
            'response_patterns': json.loads(self.response_patterns),
            'avatar_url': self.avatar_url,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }

class Evidence(db.Model):
    __tablename__ = 'evidence'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    evidence_type = db.Column(db.String(50), nullable=False)  # 'chat_log', 'screenshot', 'metadata'
    file_path = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=True)
    evidence_metadata = db.Column(db.Text, nullable=True)  # JSON string
    hash_value = db.Column(db.String(64), nullable=False)  # SHA-256 hash for integrity
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'evidence_type': self.evidence_type,
            'file_path': self.file_path,
            'content': self.content,
            'metadata': json.loads(self.evidence_metadata) if self.evidence_metadata else None,
            'hash_value': self.hash_value,
            'created_at': self.created_at.isoformat()
        }

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(100), nullable=True)  # Admin user ID
    session_id = db.Column(db.String(255), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON string
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'details': json.loads(self.details) if self.details else None,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat()
        }

