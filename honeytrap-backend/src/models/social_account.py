"""
Social Media Account Model
Handles storage and management of social media account credentials and sessions
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet
import os


class SocialAccount:
    """Model for managing social media account credentials and sessions"""
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.platform = ""
        self.username = ""
        self.email = ""
        self.display_name = ""
        self.profile_id = None  # Link to decoy profile
        self.encrypted_credentials = ""
        self.session_data = {}
        self.oauth_tokens = {}
        self.status = "inactive"  # inactive, active, suspended, error
        self.last_login = None
        self.last_activity = None
        self.login_method = "oauth"  # oauth, credentials, session
        self.capabilities = []  # post, message, comment, like, share
        self.rate_limits = {}
        self.metadata = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Initialize encryption key
        self._encryption_key = self._get_encryption_key()
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for credential storage"""
        key_file = os.path.join(os.path.dirname(__file__), '..', '..', '.encryption_key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def set_credentials(self, credentials: Dict[str, str]):
        """Encrypt and store account credentials"""
        fernet = Fernet(self._encryption_key)
        credentials_json = json.dumps(credentials)
        self.encrypted_credentials = fernet.encrypt(credentials_json.encode()).decode()
        self.updated_at = datetime.utcnow()
    
    def get_credentials(self) -> Dict[str, str]:
        """Decrypt and retrieve account credentials"""
        if not self.encrypted_credentials:
            return {}
        
        try:
            fernet = Fernet(self._encryption_key)
            decrypted_data = fernet.decrypt(self.encrypted_credentials.encode())
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Error decrypting credentials: {e}")
            return {}
    
    def set_oauth_tokens(self, tokens: Dict[str, Any]):
        """Store OAuth tokens for the account"""
        self.oauth_tokens = tokens
        self.updated_at = datetime.utcnow()
    
    def get_oauth_tokens(self) -> Dict[str, Any]:
        """Get OAuth tokens for the account"""
        return self.oauth_tokens
    
    def update_session_data(self, session_data: Dict[str, Any]):
        """Update session data for the account"""
        self.session_data.update(session_data)
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_status(self, status: str, metadata: Dict[str, Any] = None):
        """Update account status"""
        self.status = status
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if account is active and ready for use"""
        return self.status == "active"
    
    def is_session_valid(self) -> bool:
        """Check if current session is still valid"""
        if not self.last_activity:
            return False
        
        # Session expires after 24 hours of inactivity
        expiry_time = self.last_activity + timedelta(hours=24)
        return datetime.utcnow() < expiry_time
    
    def refresh_tokens_if_needed(self) -> bool:
        """Check if OAuth tokens need refreshing and refresh if possible"""
        if not self.oauth_tokens:
            return False
        
        # Check if access token is expired
        expires_at = self.oauth_tokens.get('expires_at')
        if expires_at and datetime.utcnow() > datetime.fromisoformat(expires_at):
            # Token is expired, try to refresh
            return self._refresh_oauth_tokens()
        
        return True
    
    def _refresh_oauth_tokens(self) -> bool:
        """Refresh OAuth tokens using refresh token"""
        # This would be implemented per platform
        # For now, return False to indicate refresh failed
        return False
    
    def get_rate_limit_status(self, action: str) -> Dict[str, Any]:
        """Get rate limit status for a specific action"""
        if action not in self.rate_limits:
            return {"remaining": 100, "reset_time": None, "limit": 100}
        
        return self.rate_limits[action]
    
    def update_rate_limit(self, action: str, remaining: int, reset_time: datetime, limit: int):
        """Update rate limit information for an action"""
        self.rate_limits[action] = {
            "remaining": remaining,
            "reset_time": reset_time.isoformat() if reset_time else None,
            "limit": limit
        }
        self.updated_at = datetime.utcnow()
    
    def can_perform_action(self, action: str) -> bool:
        """Check if account can perform a specific action"""
        # Check if action is in capabilities
        if action not in self.capabilities:
            return False
        
        # Check rate limits
        rate_limit = self.get_rate_limit_status(action)
        if rate_limit["remaining"] <= 0:
            reset_time = rate_limit.get("reset_time")
            if reset_time and datetime.utcnow() < datetime.fromisoformat(reset_time):
                return False
        
        return True
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert account to dictionary representation"""
        data = {
            "id": self.id,
            "platform": self.platform,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "profile_id": self.profile_id,
            "status": self.status,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "login_method": self.login_method,
            "capabilities": self.capabilities,
            "rate_limits": self.rate_limits,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "session_valid": self.is_session_valid(),
            "is_active": self.is_active()
        }
        
        if include_sensitive:
            data["credentials"] = self.get_credentials()
            data["oauth_tokens"] = self.oauth_tokens
            data["session_data"] = self.session_data
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SocialAccount':
        """Create account from dictionary representation"""
        account = cls()
        
        account.id = data.get("id", account.id)
        account.platform = data.get("platform", "")
        account.username = data.get("username", "")
        account.email = data.get("email", "")
        account.display_name = data.get("display_name", "")
        account.profile_id = data.get("profile_id")
        account.encrypted_credentials = data.get("encrypted_credentials", "")
        account.session_data = data.get("session_data", {})
        account.oauth_tokens = data.get("oauth_tokens", {})
        account.status = data.get("status", "inactive")
        account.login_method = data.get("login_method", "oauth")
        account.capabilities = data.get("capabilities", [])
        account.rate_limits = data.get("rate_limits", {})
        account.metadata = data.get("metadata", {})
        
        # Parse datetime fields
        if data.get("last_login"):
            account.last_login = datetime.fromisoformat(data["last_login"])
        if data.get("last_activity"):
            account.last_activity = datetime.fromisoformat(data["last_activity"])
        if data.get("created_at"):
            account.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            account.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return account


class SocialAccountManager:
    """Manager class for social media accounts"""
    
    def __init__(self):
        self.accounts = {}  # In-memory storage, would be database in production
    
    def create_account(self, platform: str, username: str, email: str = "", 
                      display_name: str = "", profile_id: str = None) -> SocialAccount:
        """Create a new social media account"""
        account = SocialAccount()
        account.platform = platform
        account.username = username
        account.email = email
        account.display_name = display_name or username
        account.profile_id = profile_id
        
        # Set platform-specific capabilities
        account.capabilities = self._get_platform_capabilities(platform)
        
        self.accounts[account.id] = account
        return account
    
    def get_account(self, account_id: str) -> Optional[SocialAccount]:
        """Get account by ID"""
        return self.accounts.get(account_id)
    
    def get_accounts_by_platform(self, platform: str) -> List[SocialAccount]:
        """Get all accounts for a specific platform"""
        return [acc for acc in self.accounts.values() if acc.platform == platform]
    
    def get_accounts_by_profile(self, profile_id: str) -> List[SocialAccount]:
        """Get all accounts linked to a specific profile"""
        return [acc for acc in self.accounts.values() if acc.profile_id == profile_id]
    
    def get_active_accounts(self) -> List[SocialAccount]:
        """Get all active accounts"""
        return [acc for acc in self.accounts.values() if acc.is_active()]
    
    def update_account(self, account_id: str, updates: Dict[str, Any]) -> bool:
        """Update account information"""
        account = self.get_account(account_id)
        if not account:
            return False
        
        for key, value in updates.items():
            if hasattr(account, key):
                setattr(account, key, value)
        
        account.updated_at = datetime.utcnow()
        return True
    
    def delete_account(self, account_id: str) -> bool:
        """Delete an account"""
        if account_id in self.accounts:
            del self.accounts[account_id]
            return True
        return False
    
    def _get_platform_capabilities(self, platform: str) -> List[str]:
        """Get capabilities for a specific platform"""
        platform_capabilities = {
            "discord": ["message", "join_server", "create_channel", "react"],
            "facebook": ["post", "message", "comment", "like", "share", "join_group"],
            "instagram": ["post", "story", "message", "comment", "like", "follow"],
            "tiktok": ["post", "comment", "like", "follow", "duet"],
            "snapchat": ["snap", "message", "story", "add_friend"],
            "twitter": ["tweet", "reply", "retweet", "like", "follow", "dm"],
            "linkedin": ["post", "comment", "like", "connect", "message"],
            "youtube": ["comment", "like", "subscribe", "upload"],
            "reddit": ["post", "comment", "upvote", "join_subreddit"],
            "telegram": ["message", "join_channel", "create_group"]
        }
        
        return platform_capabilities.get(platform.lower(), ["message", "post"])
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get statistics about managed accounts"""
        stats = {
            "total_accounts": len(self.accounts),
            "active_accounts": len(self.get_active_accounts()),
            "platforms": {},
            "status_distribution": {}
        }
        
        for account in self.accounts.values():
            # Platform stats
            if account.platform not in stats["platforms"]:
                stats["platforms"][account.platform] = 0
            stats["platforms"][account.platform] += 1
            
            # Status stats
            if account.status not in stats["status_distribution"]:
                stats["status_distribution"][account.status] = 0
            stats["status_distribution"][account.status] += 1
        
        return stats


# Global account manager instance
account_manager = SocialAccountManager()

