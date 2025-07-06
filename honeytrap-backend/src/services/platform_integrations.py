"""
Platform-Specific Integration Services
Handles platform-specific authentication and API interactions
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from abc import ABC, abstractmethod
import base64
import hmac
import hashlib
from urllib.parse import urlencode, quote


class PlatformIntegration(ABC):
    """Abstract base class for platform integrations"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.config = self._load_config()
    
    @abstractmethod
    def _load_config(self) -> Dict[str, str]:
        """Load platform-specific configuration"""
        pass
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get user profile information"""
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        pass
    
    @abstractmethod
    def post_content(self, access_token: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    def send_message(self, access_token: str, recipient: str, message: str) -> Dict[str, Any]:
        """Send a message to a user"""
        pass


class FacebookIntegration(PlatformIntegration):
    """Facebook/Meta platform integration"""
    
    def __init__(self):
        super().__init__("facebook")
    
    def _load_config(self) -> Dict[str, str]:
        return {
            "app_id": os.getenv("FACEBOOK_APP_ID", ""),
            "app_secret": os.getenv("FACEBOOK_APP_SECRET", ""),
            "api_version": "v18.0",
            "base_url": "https://graph.facebook.com"
        }
    
    def authenticate(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate using OAuth code"""
        if "code" not in credentials:
            raise ValueError("Authorization code required")
        
        token_url = f"{self.config['base_url']}/v{self.config['api_version']}/oauth/access_token"
        
        params = {
            "client_id": self.config["app_id"],
            "client_secret": self.config["app_secret"],
            "code": credentials["code"],
            "redirect_uri": credentials.get("redirect_uri", "")
        }
        
        response = requests.get(token_url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get Facebook user profile"""
        url = f"{self.config['base_url']}/me"
        params = {
            "access_token": access_token,
            "fields": "id,name,email,username,picture"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Facebook doesn't use refresh tokens, return long-lived token"""
        url = f"{self.config['base_url']}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.config["app_id"],
            "client_secret": self.config["app_secret"],
            "fb_exchange_token": refresh_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def post_content(self, access_token: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to Facebook"""
        # Get user's pages first
        pages_url = f"{self.config['base_url']}/me/accounts"
        pages_response = requests.get(pages_url, params={"access_token": access_token})
        pages_response.raise_for_status()
        
        pages = pages_response.json().get("data", [])
        if not pages:
            # Post to user's timeline
            post_url = f"{self.config['base_url']}/me/feed"
        else:
            # Post to first page
            page_id = pages[0]["id"]
            page_token = pages[0]["access_token"]
            post_url = f"{self.config['base_url']}/{page_id}/feed"
            access_token = page_token
        
        post_data = {
            "message": content.get("text", ""),
            "access_token": access_token
        }
        
        if content.get("image_url"):
            post_data["picture"] = content["image_url"]
        
        response = requests.post(post_url, data=post_data)
        response.raise_for_status()
        
        return response.json()
    
    def send_message(self, access_token: str, recipient: str, message: str) -> Dict[str, Any]:
        """Send message via Facebook Messenger"""
        url = f"{self.config['base_url']}/me/messages"
        
        message_data = {
            "recipient": {"id": recipient},
            "message": {"text": message},
            "access_token": access_token
        }
        
        response = requests.post(url, json=message_data)
        response.raise_for_status()
        
        return response.json()


class InstagramIntegration(PlatformIntegration):
    """Instagram platform integration"""
    
    def __init__(self):
        super().__init__("instagram")
    
    def _load_config(self) -> Dict[str, str]:
        return {
            "app_id": os.getenv("INSTAGRAM_APP_ID", ""),
            "app_secret": os.getenv("INSTAGRAM_APP_SECRET", ""),
            "base_url": "https://graph.instagram.com"
        }
    
    def authenticate(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate using OAuth code"""
        token_url = f"{self.config['base_url']}/oauth/access_token"
        
        data = {
            "client_id": self.config["app_id"],
            "client_secret": self.config["app_secret"],
            "grant_type": "authorization_code",
            "redirect_uri": credentials.get("redirect_uri", ""),
            "code": credentials["code"]
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get Instagram user profile"""
        url = f"{self.config['base_url']}/me"
        params = {
            "fields": "id,username,account_type",
            "access_token": access_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Instagram access token"""
        url = f"{self.config['base_url']}/refresh_access_token"
        params = {
            "grant_type": "ig_refresh_token",
            "access_token": refresh_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def post_content(self, access_token: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to Instagram"""
        # Instagram requires media to be uploaded first
        if not content.get("image_url"):
            raise ValueError("Instagram posts require an image")
        
        # Create media object
        media_url = f"{self.config['base_url']}/me/media"
        media_data = {
            "image_url": content["image_url"],
            "caption": content.get("text", ""),
            "access_token": access_token
        }
        
        media_response = requests.post(media_url, data=media_data)
        media_response.raise_for_status()
        
        media_id = media_response.json()["id"]
        
        # Publish media
        publish_url = f"{self.config['base_url']}/me/media_publish"
        publish_data = {
            "creation_id": media_id,
            "access_token": access_token
        }
        
        response = requests.post(publish_url, data=publish_data)
        response.raise_for_status()
        
        return response.json()
    
    def send_message(self, access_token: str, recipient: str, message: str) -> Dict[str, Any]:
        """Instagram doesn't support direct messaging via API"""
        raise NotImplementedError("Instagram direct messaging not supported via API")


class TwitterIntegration(PlatformIntegration):
    """Twitter/X platform integration"""
    
    def __init__(self):
        super().__init__("twitter")
    
    def _load_config(self) -> Dict[str, str]:
        return {
            "api_key": os.getenv("TWITTER_API_KEY", ""),
            "api_secret": os.getenv("TWITTER_API_SECRET", ""),
            "bearer_token": os.getenv("TWITTER_BEARER_TOKEN", ""),
            "base_url": "https://api.twitter.com/2"
        }
    
    def authenticate(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate using OAuth 2.0"""
        token_url = "https://api.twitter.com/2/oauth2/token"
        
        # Encode credentials
        credentials_encoded = base64.b64encode(
            f"{self.config['api_key']}:{self.config['api_secret']}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {credentials_encoded}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": credentials["code"],
            "redirect_uri": credentials.get("redirect_uri", ""),
            "code_verifier": credentials.get("code_verifier", "")
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get Twitter user profile"""
        url = f"{self.config['base_url']}/users/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"user.fields": "id,name,username,profile_image_url"}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Twitter access token"""
        token_url = "https://api.twitter.com/2/oauth2/token"
        
        credentials_encoded = base64.b64encode(
            f"{self.config['api_key']}:{self.config['api_secret']}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {credentials_encoded}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        
        return response.json()
    
    def post_content(self, access_token: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post tweet to Twitter"""
        url = f"{self.config['base_url']}/tweets"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        tweet_data = {"text": content.get("text", "")}
        
        response = requests.post(url, headers=headers, json=tweet_data)
        response.raise_for_status()
        
        return response.json()
    
    def send_message(self, access_token: str, recipient: str, message: str) -> Dict[str, Any]:
        """Send direct message on Twitter"""
        url = f"{self.config['base_url']}/dm_conversations/with/{recipient}/messages"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        message_data = {
            "text": message,
            "media_id": None  # Optional media attachment
        }
        
        response = requests.post(url, headers=headers, json=message_data)
        response.raise_for_status()
        
        return response.json()


class DiscordIntegration(PlatformIntegration):
    """Discord platform integration"""
    
    def __init__(self):
        super().__init__("discord")
    
    def _load_config(self) -> Dict[str, str]:
        return {
            "client_id": os.getenv("DISCORD_CLIENT_ID", ""),
            "client_secret": os.getenv("DISCORD_CLIENT_SECRET", ""),
            "bot_token": os.getenv("DISCORD_BOT_TOKEN", ""),
            "base_url": "https://discord.com/api/v10"
        }
    
    def authenticate(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate using OAuth code"""
        token_url = f"{self.config['base_url']}/oauth2/token"
        
        data = {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "grant_type": "authorization_code",
            "code": credentials["code"],
            "redirect_uri": credentials.get("redirect_uri", "")
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get Discord user profile"""
        url = f"{self.config['base_url']}/users/@me"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Discord access token"""
        token_url = f"{self.config['base_url']}/oauth2/token"
        
        data = {
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def post_content(self, access_token: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post message to Discord channel"""
        # This requires knowing the channel ID
        channel_id = content.get("channel_id")
        if not channel_id:
            raise ValueError("Discord posting requires channel_id")
        
        url = f"{self.config['base_url']}/channels/{channel_id}/messages"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        message_data = {"content": content.get("text", "")}
        
        response = requests.post(url, headers=headers, json=message_data)
        response.raise_for_status()
        
        return response.json()
    
    def send_message(self, access_token: str, recipient: str, message: str) -> Dict[str, Any]:
        """Send direct message on Discord"""
        # First create DM channel
        dm_url = f"{self.config['base_url']}/users/@me/channels"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        dm_data = {"recipient_id": recipient}
        dm_response = requests.post(dm_url, headers=headers, json=dm_data)
        dm_response.raise_for_status()
        
        channel_id = dm_response.json()["id"]
        
        # Send message to DM channel
        message_url = f"{self.config['base_url']}/channels/{channel_id}/messages"
        message_data = {"content": message}
        
        response = requests.post(message_url, headers=headers, json=message_data)
        response.raise_for_status()
        
        return response.json()


class PlatformIntegrationManager:
    """Manager for all platform integrations"""
    
    def __init__(self):
        self.integrations = {
            "facebook": FacebookIntegration(),
            "instagram": InstagramIntegration(),
            "twitter": TwitterIntegration(),
            "discord": DiscordIntegration()
        }
    
    def get_integration(self, platform: str) -> Optional[PlatformIntegration]:
        """Get integration for a specific platform"""
        return self.integrations.get(platform.lower())
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return list(self.integrations.keys())
    
    def authenticate_account(self, platform: str, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Authenticate account on a platform"""
        integration = self.get_integration(platform)
        if not integration:
            raise ValueError(f"Platform {platform} not supported")
        
        return integration.authenticate(credentials)
    
    def get_user_profile(self, platform: str, access_token: str) -> Dict[str, Any]:
        """Get user profile for a platform"""
        integration = self.get_integration(platform)
        if not integration:
            raise ValueError(f"Platform {platform} not supported")
        
        return integration.get_user_profile(access_token)
    
    def refresh_token(self, platform: str, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token for a platform"""
        integration = self.get_integration(platform)
        if not integration:
            raise ValueError(f"Platform {platform} not supported")
        
        return integration.refresh_token(refresh_token)
    
    def post_content(self, platform: str, access_token: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Post content to a platform"""
        integration = self.get_integration(platform)
        if not integration:
            raise ValueError(f"Platform {platform} not supported")
        
        return integration.post_content(access_token, content)
    
    def send_message(self, platform: str, access_token: str, recipient: str, message: str) -> Dict[str, Any]:
        """Send message on a platform"""
        integration = self.get_integration(platform)
        if not integration:
            raise ValueError(f"Platform {platform} not supported")
        
        return integration.send_message(access_token, recipient, message)
    
    def test_platform_connection(self, platform: str, access_token: str) -> Dict[str, Any]:
        """Test connection to a platform"""
        try:
            profile = self.get_user_profile(platform, access_token)
            return {
                "success": True,
                "platform": platform,
                "user_id": profile.get("id"),
                "username": profile.get("username") or profile.get("name"),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "platform": platform,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global platform integration manager
platform_manager = PlatformIntegrationManager()

