from src.models.user import db
from datetime import datetime
import json
import uuid

class DecoyProfile(db.Model):
    """Model for managing decoy profiles across platforms"""
    __tablename__ = 'decoy_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Basic Profile Information
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    
    # Platform Information
    platform_type = db.Column(db.String(20), nullable=False)  # discord, facebook, instagram, etc.
    platform_profile_id = db.Column(db.String(100), nullable=True)  # actual platform ID when deployed
    profile_url = db.Column(db.String(255), nullable=True)
    
    # Profile Content
    bio = db.Column(db.Text, nullable=True)
    interests = db.Column(db.Text, nullable=True)  # JSON string
    backstory = db.Column(db.Text, nullable=True)
    
    # Visual Assets
    profile_image_url = db.Column(db.String(255), nullable=True)
    cover_image_url = db.Column(db.String(255), nullable=True)
    additional_images = db.Column(db.Text, nullable=True)  # JSON array of image URLs
    
    # Deployment Status
    status = db.Column(db.String(20), default='created')  # created, deployed, active, suspended
    deployment_date = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)
    
    # Analytics
    contact_attempts = db.Column(db.Integer, default=0)
    successful_engagements = db.Column(db.Integer, default=0)
    evidence_captured = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(100), nullable=True)  # Officer ID
    
    def to_dict(self):
        return {
            'id': self.id,
            'profile_uuid': self.profile_uuid,
            'name': self.name,
            'username': self.username,
            'age': self.age,
            'location': self.location,
            'platform_type': self.platform_type,
            'platform_profile_id': self.platform_profile_id,
            'profile_url': self.profile_url,
            'bio': self.bio,
            'interests': json.loads(self.interests) if self.interests else [],
            'backstory': self.backstory,
            'profile_image_url': self.profile_image_url,
            'cover_image_url': self.cover_image_url,
            'additional_images': json.loads(self.additional_images) if self.additional_images else [],
            'status': self.status,
            'deployment_date': self.deployment_date.isoformat() if self.deployment_date else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'contact_attempts': self.contact_attempts,
            'successful_engagements': self.successful_engagements,
            'evidence_captured': self.evidence_captured,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': self.created_by
        }

class ProfileContent(db.Model):
    """Model for managing profile content and posts"""
    __tablename__ = 'profile_content'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('decoy_profiles.id'), nullable=False)
    
    # Content Information
    content_type = db.Column(db.String(20), nullable=False)  # post, story, bio_update, etc.
    platform_type = db.Column(db.String(20), nullable=False)
    content_text = db.Column(db.Text, nullable=True)
    content_media = db.Column(db.Text, nullable=True)  # JSON array of media URLs
    
    # Scheduling
    scheduled_time = db.Column(db.DateTime, nullable=True)
    posted_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, posted, failed
    
    # Engagement
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    profile = db.relationship('DecoyProfile', backref=db.backref('content', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'content_type': self.content_type,
            'platform_type': self.platform_type,
            'content_text': self.content_text,
            'content_media': json.loads(self.content_media) if self.content_media else [],
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'posted_time': self.posted_time.isoformat() if self.posted_time else None,
            'status': self.status,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'shares_count': self.shares_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ProfileAnalytics(db.Model):
    """Model for tracking profile performance and discovery metrics"""
    __tablename__ = 'profile_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('decoy_profiles.id'), nullable=False)
    
    # Discovery Metrics
    profile_views = db.Column(db.Integer, default=0)
    search_appearances = db.Column(db.Integer, default=0)
    friend_requests = db.Column(db.Integer, default=0)
    follow_requests = db.Column(db.Integer, default=0)
    
    # Engagement Metrics
    messages_received = db.Column(db.Integer, default=0)
    suspicious_contacts = db.Column(db.Integer, default=0)
    threat_level_1 = db.Column(db.Integer, default=0)
    threat_level_2 = db.Column(db.Integer, default=0)
    threat_level_3 = db.Column(db.Integer, default=0)
    
    # Geographic Data
    contact_locations = db.Column(db.Text, nullable=True)  # JSON array of locations
    
    # Time-based Data
    date_recorded = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    profile = db.relationship('DecoyProfile', backref=db.backref('analytics', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'profile_views': self.profile_views,
            'search_appearances': self.search_appearances,
            'friend_requests': self.friend_requests,
            'follow_requests': self.follow_requests,
            'messages_received': self.messages_received,
            'suspicious_contacts': self.suspicious_contacts,
            'threat_level_1': self.threat_level_1,
            'threat_level_2': self.threat_level_2,
            'threat_level_3': self.threat_level_3,
            'contact_locations': json.loads(self.contact_locations) if self.contact_locations else [],
            'date_recorded': self.date_recorded.isoformat(),
            'created_at': self.created_at.isoformat()
        }

