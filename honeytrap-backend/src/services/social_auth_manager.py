"""
Social Media Authentication Manager
Handles authentication and login processes for various social media platforms
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlencode, parse_qs, urlparse
import secrets
import hashlib

from models.social_account import SocialAccount, account_manager


class SocialAuthManager:
    """Manages authentication for social media platforms"""
    
    def __init__(self):
        self.oauth_configs = self._load_oauth_configs()
        self.active_sessions = {}  # Store active browser sessions
        self.auth_states = {}  # Store OAuth state parameters
    
    def _load_oauth_configs(self) -> Dict[str, Dict[str, str]]:
        """Load OAuth configuration for different platforms"""
        return {
            "facebook": {
                "client_id": os.getenv("FACEBOOK_CLIENT_ID", ""),
                "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET", ""),
                "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "scope": "email,public_profile,pages_manage_posts,pages_read_engagement",
                "redirect_uri": "http://localhost:5000/api/auth/callback/facebook"
            },
            "instagram": {
                "client_id": os.getenv("INSTAGRAM_CLIENT_ID", ""),
                "client_secret": os.getenv("INSTAGRAM_CLIENT_SECRET", ""),
                "auth_url": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "scope": "user_profile,user_media",
                "redirect_uri": "http://localhost:5000/api/auth/callback/instagram"
            },
            "twitter": {
                "client_id": os.getenv("TWITTER_CLIENT_ID", ""),
                "client_secret": os.getenv("TWITTER_CLIENT_SECRET", ""),
                "auth_url": "https://twitter.com/i/oauth2/authorize",
                "token_url": "https://api.twitter.com/2/oauth2/token",
                "scope": "tweet.read tweet.write users.read follows.read follows.write",
                "redirect_uri": "http://localhost:5000/api/auth/callback/twitter"
            },
            "linkedin": {
                "client_id": os.getenv("LINKEDIN_CLIENT_ID", ""),
                "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", ""),
                "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
                "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
                "scope": "r_liteprofile r_emailaddress w_member_social",
                "redirect_uri": "http://localhost:5000/api/auth/callback/linkedin"
            },
            "google": {
                "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "scope": "openid email profile",
                "redirect_uri": "http://localhost:5000/api/auth/callback/google"
            }
        }
    
    def get_oauth_url(self, platform: str, account_id: str = None) -> Tuple[str, str]:
        """Generate OAuth authorization URL for a platform"""
        if platform not in self.oauth_configs:
            raise ValueError(f"Platform {platform} not supported")
        
        config = self.oauth_configs[platform]
        
        # Generate state parameter for security
        state = secrets.token_urlsafe(32)
        self.auth_states[state] = {
            "platform": platform,
            "account_id": account_id,
            "timestamp": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        
        # Build authorization URL
        params = {
            "client_id": config["client_id"],
            "redirect_uri": config["redirect_uri"],
            "scope": config["scope"],
            "response_type": "code",
            "state": state
        }
        
        # Platform-specific parameters
        if platform == "facebook":
            params["display"] = "popup"
        elif platform == "google":
            params["access_type"] = "offline"
            params["prompt"] = "consent"
        
        auth_url = f"{config['auth_url']}?{urlencode(params)}"
        return auth_url, state
    
    def handle_oauth_callback(self, platform: str, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for tokens"""
        # Verify state parameter
        if state not in self.auth_states:
            raise ValueError("Invalid state parameter")
        
        state_data = self.auth_states[state]
        if datetime.utcnow() > state_data["expires_at"]:
            del self.auth_states[state]
            raise ValueError("State parameter expired")
        
        if state_data["platform"] != platform:
            raise ValueError("Platform mismatch")
        
        # Exchange code for tokens
        config = self.oauth_configs[platform]
        token_data = self._exchange_code_for_tokens(platform, code, config)
        
        # Get user profile information
        profile_data = self._get_user_profile(platform, token_data["access_token"])
        
        # Create or update account
        account_id = state_data.get("account_id")
        if account_id:
            account = account_manager.get_account(account_id)
            if not account:
                raise ValueError("Account not found")
        else:
            # Create new account
            account = account_manager.create_account(
                platform=platform,
                username=profile_data.get("username", ""),
                email=profile_data.get("email", ""),
                display_name=profile_data.get("display_name", "")
            )
        
        # Store OAuth tokens
        account.set_oauth_tokens({
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_at": (datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))).isoformat(),
            "scope": token_data.get("scope", config["scope"])
        })
        
        # Update account status and metadata
        account.set_status("active", {
            "login_method": "oauth",
            "last_oauth_login": datetime.utcnow().isoformat(),
            "profile_data": profile_data
        })
        account.last_login = datetime.utcnow()
        
        # Clean up state
        del self.auth_states[state]
        
        return {
            "success": True,
            "account_id": account.id,
            "platform": platform,
            "username": account.username,
            "display_name": account.display_name
        }
    
    def _exchange_code_for_tokens(self, platform: str, code: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        data = {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "code": code,
            "redirect_uri": config["redirect_uri"],
            "grant_type": "authorization_code"
        }
        
        response = requests.post(config["token_url"], data=data)
        response.raise_for_status()
        
        return response.json()
    
    def _get_user_profile(self, platform: str, access_token: str) -> Dict[str, Any]:
        """Get user profile information using access token"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        profile_urls = {
            "facebook": "https://graph.facebook.com/me?fields=id,name,email,username",
            "instagram": "https://graph.instagram.com/me?fields=id,username,account_type",
            "twitter": "https://api.twitter.com/2/users/me",
            "linkedin": "https://api.linkedin.com/v2/people/~",
            "google": "https://www.googleapis.com/oauth2/v2/userinfo"
        }
        
        if platform not in profile_urls:
            return {}
        
        response = requests.get(profile_urls[platform], headers=headers)
        response.raise_for_status()
        
        profile_data = response.json()
        
        # Normalize profile data across platforms
        normalized = {
            "platform_id": profile_data.get("id"),
            "username": profile_data.get("username") or profile_data.get("screen_name"),
            "display_name": profile_data.get("name") or profile_data.get("displayName"),
            "email": profile_data.get("email"),
            "profile_url": self._get_profile_url(platform, profile_data),
            "raw_data": profile_data
        }
        
        return normalized
    
    def _get_profile_url(self, platform: str, profile_data: Dict[str, Any]) -> str:
        """Generate profile URL for the platform"""
        platform_urls = {
            "facebook": f"https://facebook.com/{profile_data.get('id')}",
            "instagram": f"https://instagram.com/{profile_data.get('username')}",
            "twitter": f"https://twitter.com/{profile_data.get('username')}",
            "linkedin": f"https://linkedin.com/in/{profile_data.get('id')}",
        }
        
        return platform_urls.get(platform, "")
    
    def login_with_credentials(self, platform: str, username: str, password: str, 
                             account_id: str = None) -> Dict[str, Any]:
        """Login using username/password credentials (for platforms that support it)"""
        # This would typically use browser automation for platforms without API login
        # For security and compliance, this should be implemented carefully
        
        if account_id:
            account = account_manager.get_account(account_id)
            if not account:
                raise ValueError("Account not found")
        else:
            account = account_manager.create_account(
                platform=platform,
                username=username
            )
        
        # Store encrypted credentials
        account.set_credentials({
            "username": username,
            "password": password
        })
        
        # For now, mark as active (in real implementation, would verify login)
        account.set_status("active", {
            "login_method": "credentials",
            "last_credential_login": datetime.utcnow().isoformat()
        })
        account.last_login = datetime.utcnow()
        
        return {
            "success": True,
            "account_id": account.id,
            "platform": platform,
            "username": account.username,
            "login_method": "credentials"
        }
    
    def refresh_account_tokens(self, account_id: str) -> bool:
        """Refresh OAuth tokens for an account"""
        account = account_manager.get_account(account_id)
        if not account:
            return False
        
        tokens = account.get_oauth_tokens()
        if not tokens or not tokens.get("refresh_token"):
            return False
        
        config = self.oauth_configs.get(account.platform)
        if not config:
            return False
        
        try:
            # Refresh tokens
            data = {
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "refresh_token": tokens["refresh_token"],
                "grant_type": "refresh_token"
            }
            
            response = requests.post(config["token_url"], data=data)
            response.raise_for_status()
            
            new_tokens = response.json()
            
            # Update stored tokens
            updated_tokens = tokens.copy()
            updated_tokens.update({
                "access_token": new_tokens["access_token"],
                "expires_at": (datetime.utcnow() + timedelta(seconds=new_tokens.get("expires_in", 3600))).isoformat()
            })
            
            if "refresh_token" in new_tokens:
                updated_tokens["refresh_token"] = new_tokens["refresh_token"]
            
            account.set_oauth_tokens(updated_tokens)
            return True
            
        except Exception as e:
            print(f"Error refreshing tokens for account {account_id}: {e}")
            return False
    
    def logout_account(self, account_id: str) -> bool:
        """Logout an account and clear session data"""
        account = account_manager.get_account(account_id)
        if not account:
            return False
        
        # Clear sensitive data
        account.oauth_tokens = {}
        account.session_data = {}
        account.set_status("inactive", {
            "logout_time": datetime.utcnow().isoformat()
        })
        
        return True
    
    def get_account_capabilities(self, account_id: str) -> List[str]:
        """Get available capabilities for an account"""
        account = account_manager.get_account(account_id)
        if not account or not account.is_active():
            return []
        
        return account.capabilities
    
    def test_account_connection(self, account_id: str) -> Dict[str, Any]:
        """Test if account connection is still valid"""
        account = account_manager.get_account(account_id)
        if not account:
            return {"valid": False, "error": "Account not found"}
        
        if not account.is_active():
            return {"valid": False, "error": "Account not active"}
        
        # Test OAuth token validity
        tokens = account.get_oauth_tokens()
        if tokens and tokens.get("access_token"):
            try:
                profile_data = self._get_user_profile(account.platform, tokens["access_token"])
                account.last_activity = datetime.utcnow()
                return {
                    "valid": True,
                    "platform": account.platform,
                    "username": account.username,
                    "last_activity": account.last_activity.isoformat()
                }
            except Exception as e:
                account.set_status("error", {"connection_error": str(e)})
                return {"valid": False, "error": f"Connection test failed: {e}"}
        
        return {"valid": False, "error": "No valid tokens"}
    
    def get_supported_platforms(self) -> List[Dict[str, Any]]:
        """Get list of supported platforms and their capabilities"""
        platforms = []
        
        for platform, config in self.oauth_configs.items():
            platforms.append({
                "name": platform,
                "display_name": platform.title(),
                "oauth_available": bool(config.get("client_id")),
                "capabilities": account_manager._get_platform_capabilities(platform),
                "auth_methods": ["oauth", "credentials"] if platform in ["discord", "telegram"] else ["oauth"]
            })
        
        return platforms
    
    def cleanup_expired_states(self):
        """Clean up expired OAuth states"""
        current_time = datetime.utcnow()
        expired_states = [
            state for state, data in self.auth_states.items()
            if current_time > data["expires_at"]
        ]
        
        for state in expired_states:
            del self.auth_states[state]


# Global auth manager instance
auth_manager = SocialAuthManager()

