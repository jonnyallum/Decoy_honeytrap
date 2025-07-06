"""
Session Management Service
Handles multiple active social media sessions and account switching
"""

import os
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from threading import Lock
import pickle

from models.social_account import account_manager, SocialAccount
from services.social_auth_manager import auth_manager
from services.browser_automation import browser_service
from services.platform_integrations import platform_manager


class SessionManager:
    """Manages multiple active social media sessions"""
    
    def __init__(self):
        self.active_sessions = {}  # session_id -> session_data
        self.user_sessions = {}    # user_id -> list of session_ids
        self.account_sessions = {} # account_id -> session_id
        self.session_lock = Lock()
        self.session_timeout = 3600  # 1 hour default timeout
        
        # Session storage directory
        self.sessions_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'sessions')
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def create_session(self, user_id: str, account_id: str, session_type: str = "api") -> str:
        """Create a new session for a user and account"""
        with self.session_lock:
            # Check if account already has an active session
            if account_id in self.account_sessions:
                existing_session_id = self.account_sessions[account_id]
                if self.is_session_active(existing_session_id):
                    return existing_session_id
                else:
                    # Clean up expired session
                    self.close_session(existing_session_id)
            
            # Get account information
            account = account_manager.get_account(account_id)
            if not account:
                raise ValueError("Account not found")
            
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Create session data
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "account_id": account_id,
                "platform": account.platform,
                "session_type": session_type,  # api, browser, hybrid
                "status": "initializing",
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(seconds=self.session_timeout),
                "metadata": {},
                "browser_session_id": None,
                "api_tokens": {},
                "capabilities": account.capabilities.copy(),
                "rate_limits": {},
                "activity_log": []
            }
            
            # Store session
            self.active_sessions[session_id] = session_data
            
            # Update user sessions
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(session_id)
            
            # Update account sessions
            self.account_sessions[account_id] = session_id
            
            # Initialize session based on type
            if session_type == "browser":
                self._initialize_browser_session(session_id, account)
            elif session_type == "api":
                self._initialize_api_session(session_id, account)
            elif session_type == "hybrid":
                self._initialize_hybrid_session(session_id, account)
            
            # Save session to disk
            self._save_session(session_id)
            
            return session_id
    
    def _initialize_browser_session(self, session_id: str, account: SocialAccount):
        """Initialize a browser-based session"""
        try:
            # Create browser session
            browser_session_id = browser_service.create_browser_session(
                account.id, 
                account.platform,
                headless=True
            )
            
            # Update session data
            session_data = self.active_sessions[session_id]
            session_data["browser_session_id"] = browser_session_id
            session_data["status"] = "active"
            
            # Try to restore saved session
            if browser_service.restore_session(browser_session_id, account.platform):
                session_data["metadata"]["session_restored"] = True
            else:
                # Need to login
                credentials = account.get_credentials()
                if credentials and credentials.get("username") and credentials.get("password"):
                    login_result = self._perform_browser_login(browser_session_id, account, credentials)
                    session_data["metadata"]["login_result"] = login_result
            
            self._log_activity(session_id, "browser_session_initialized", {
                "browser_session_id": browser_session_id
            })
            
        except Exception as e:
            session_data = self.active_sessions[session_id]
            session_data["status"] = "error"
            session_data["metadata"]["error"] = str(e)
            self._log_activity(session_id, "browser_session_error", {"error": str(e)})
    
    def _initialize_api_session(self, session_id: str, account: SocialAccount):
        """Initialize an API-based session"""
        try:
            # Get OAuth tokens
            tokens = account.get_oauth_tokens()
            if tokens and tokens.get("access_token"):
                # Test token validity
                test_result = platform_manager.test_platform_connection(
                    account.platform, 
                    tokens["access_token"]
                )
                
                session_data = self.active_sessions[session_id]
                session_data["api_tokens"] = tokens
                
                if test_result["success"]:
                    session_data["status"] = "active"
                    session_data["metadata"]["token_valid"] = True
                else:
                    # Try to refresh token
                    if auth_manager.refresh_account_tokens(account.id):
                        refreshed_tokens = account.get_oauth_tokens()
                        session_data["api_tokens"] = refreshed_tokens
                        session_data["status"] = "active"
                        session_data["metadata"]["token_refreshed"] = True
                    else:
                        session_data["status"] = "error"
                        session_data["metadata"]["error"] = "Token refresh failed"
            else:
                session_data = self.active_sessions[session_id]
                session_data["status"] = "error"
                session_data["metadata"]["error"] = "No valid tokens available"
            
            self._log_activity(session_id, "api_session_initialized", {
                "token_available": bool(tokens)
            })
            
        except Exception as e:
            session_data = self.active_sessions[session_id]
            session_data["status"] = "error"
            session_data["metadata"]["error"] = str(e)
            self._log_activity(session_id, "api_session_error", {"error": str(e)})
    
    def _initialize_hybrid_session(self, session_id: str, account: SocialAccount):
        """Initialize a hybrid session (both browser and API)"""
        # Initialize both browser and API sessions
        self._initialize_browser_session(session_id, account)
        self._initialize_api_session(session_id, account)
        
        session_data = self.active_sessions[session_id]
        session_data["session_type"] = "hybrid"
        
        self._log_activity(session_id, "hybrid_session_initialized", {})
    
    def _perform_browser_login(self, browser_session_id: str, account: SocialAccount, credentials: Dict[str, str]) -> Dict[str, Any]:
        """Perform browser login for an account"""
        platform = account.platform.lower()
        username = credentials.get("username", "")
        password = credentials.get("password", "")
        
        if platform == "facebook":
            return browser_service.login_facebook(browser_session_id, username, password)
        elif platform == "instagram":
            return browser_service.login_instagram(browser_session_id, username, password)
        elif platform == "tiktok":
            return browser_service.login_tiktok(browser_session_id, username, password)
        elif platform == "snapchat":
            return browser_service.login_snapchat(browser_session_id, username, password)
        else:
            return {"success": False, "error": f"Browser login not supported for {platform}"}
    
    def switch_session(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Switch to a different session for a user"""
        with self.session_lock:
            # Verify session belongs to user
            if user_id not in self.user_sessions or session_id not in self.user_sessions[user_id]:
                raise ValueError("Session not found or access denied")
            
            # Check if session is active
            if not self.is_session_active(session_id):
                raise ValueError("Session is not active")
            
            # Update last activity
            session_data = self.active_sessions[session_id]
            session_data["last_activity"] = datetime.utcnow()
            
            # Get account information
            account = account_manager.get_account(session_data["account_id"])
            
            self._log_activity(session_id, "session_switched", {"user_id": user_id})
            
            return {
                "session_id": session_id,
                "account_id": session_data["account_id"],
                "platform": session_data["platform"],
                "status": session_data["status"],
                "session_type": session_data["session_type"],
                "capabilities": session_data["capabilities"],
                "account_info": account.to_dict() if account else None
            }
    
    def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        if user_id not in self.user_sessions:
            return []
        
        sessions = []
        for session_id in self.user_sessions[user_id]:
            if self.is_session_active(session_id):
                session_data = self.active_sessions[session_id]
                account = account_manager.get_account(session_data["account_id"])
                
                sessions.append({
                    "session_id": session_id,
                    "account_id": session_data["account_id"],
                    "platform": session_data["platform"],
                    "status": session_data["status"],
                    "session_type": session_data["session_type"],
                    "created_at": session_data["created_at"].isoformat(),
                    "last_activity": session_data["last_activity"].isoformat(),
                    "account_username": account.username if account else "Unknown",
                    "account_display_name": account.display_name if account else "Unknown"
                })
        
        return sessions
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a session"""
        if session_id not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[session_id]
        account = account_manager.get_account(session_data["account_id"])
        
        # Get browser session status if applicable
        browser_status = None
        if session_data.get("browser_session_id"):
            browser_status = browser_service.get_session_status(session_data["browser_session_id"])
        
        return {
            "session_id": session_id,
            "user_id": session_data["user_id"],
            "account_id": session_data["account_id"],
            "platform": session_data["platform"],
            "session_type": session_data["session_type"],
            "status": session_data["status"],
            "created_at": session_data["created_at"].isoformat(),
            "last_activity": session_data["last_activity"].isoformat(),
            "expires_at": session_data["expires_at"].isoformat(),
            "capabilities": session_data["capabilities"],
            "rate_limits": session_data["rate_limits"],
            "metadata": session_data["metadata"],
            "browser_status": browser_status,
            "account_info": account.to_dict() if account else None,
            "activity_log": session_data["activity_log"][-10:]  # Last 10 activities
        }
    
    def perform_action(self, session_id: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform an action using a session"""
        if not self.is_session_active(session_id):
            raise ValueError("Session is not active")
        
        session_data = self.active_sessions[session_id]
        account = account_manager.get_account(session_data["account_id"])
        
        if not account:
            raise ValueError("Account not found")
        
        # Check if action is supported
        if action not in session_data["capabilities"]:
            raise ValueError(f"Action '{action}' not supported for this account")
        
        # Check rate limits
        if not self._check_rate_limit(session_id, action):
            raise ValueError(f"Rate limit exceeded for action '{action}'")
        
        # Update last activity
        session_data["last_activity"] = datetime.utcnow()
        
        # Perform action based on session type
        result = None
        if session_data["session_type"] in ["api", "hybrid"]:
            result = self._perform_api_action(session_id, action, parameters)
        
        if not result and session_data["session_type"] in ["browser", "hybrid"]:
            result = self._perform_browser_action(session_id, action, parameters)
        
        # Log activity
        self._log_activity(session_id, f"action_{action}", {
            "parameters": parameters,
            "result": result
        })
        
        # Update rate limits
        self._update_rate_limit(session_id, action)
        
        return result or {"success": False, "error": "Action not performed"}
    
    def _perform_api_action(self, session_id: str, action: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Perform action using API"""
        session_data = self.active_sessions[session_id]
        tokens = session_data.get("api_tokens", {})
        access_token = tokens.get("access_token")
        
        if not access_token:
            return None
        
        try:
            if action == "post":
                return platform_manager.post_content(
                    session_data["platform"],
                    access_token,
                    parameters
                )
            elif action == "message":
                return platform_manager.send_message(
                    session_data["platform"],
                    access_token,
                    parameters.get("recipient", ""),
                    parameters.get("message", "")
                )
            else:
                return None
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _perform_browser_action(self, session_id: str, action: str, parameters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Perform action using browser automation"""
        session_data = self.active_sessions[session_id]
        browser_session_id = session_data.get("browser_session_id")
        
        if not browser_session_id:
            return None
        
        # Browser actions would be implemented here
        # For now, return a placeholder
        return {"success": True, "method": "browser", "action": action}
    
    def _check_rate_limit(self, session_id: str, action: str) -> bool:
        """Check if action is within rate limits"""
        session_data = self.active_sessions[session_id]
        rate_limits = session_data.get("rate_limits", {})
        
        if action not in rate_limits:
            return True
        
        limit_data = rate_limits[action]
        current_time = datetime.utcnow()
        
        # Check if rate limit window has reset
        if "reset_time" in limit_data:
            reset_time = datetime.fromisoformat(limit_data["reset_time"])
            if current_time > reset_time:
                # Reset the limit
                limit_data["count"] = 0
                limit_data["reset_time"] = (current_time + timedelta(hours=1)).isoformat()
        
        # Check if under limit
        return limit_data.get("count", 0) < limit_data.get("limit", 100)
    
    def _update_rate_limit(self, session_id: str, action: str):
        """Update rate limit counter for an action"""
        session_data = self.active_sessions[session_id]
        rate_limits = session_data.setdefault("rate_limits", {})
        
        if action not in rate_limits:
            rate_limits[action] = {
                "count": 0,
                "limit": 100,  # Default limit
                "reset_time": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        
        rate_limits[action]["count"] += 1
    
    def _log_activity(self, session_id: str, activity_type: str, data: Dict[str, Any]):
        """Log activity for a session"""
        session_data = self.active_sessions[session_id]
        activity_log = session_data.setdefault("activity_log", [])
        
        activity_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": activity_type,
            "data": data
        })
        
        # Keep only last 100 activities
        if len(activity_log) > 100:
            session_data["activity_log"] = activity_log[-100:]
    
    def is_session_active(self, session_id: str) -> bool:
        """Check if a session is active"""
        if session_id not in self.active_sessions:
            return False
        
        session_data = self.active_sessions[session_id]
        current_time = datetime.utcnow()
        
        # Check if session has expired
        if current_time > session_data["expires_at"]:
            return False
        
        # Check if session status is active
        return session_data["status"] == "active"
    
    def extend_session(self, session_id: str, extension_seconds: int = 3600) -> bool:
        """Extend session timeout"""
        if session_id not in self.active_sessions:
            return False
        
        session_data = self.active_sessions[session_id]
        session_data["expires_at"] = datetime.utcnow() + timedelta(seconds=extension_seconds)
        session_data["last_activity"] = datetime.utcnow()
        
        self._save_session(session_id)
        return True
    
    def close_session(self, session_id: str) -> bool:
        """Close a session"""
        with self.session_lock:
            if session_id not in self.active_sessions:
                return False
            
            session_data = self.active_sessions[session_id]
            
            # Close browser session if exists
            if session_data.get("browser_session_id"):
                browser_service.close_session(session_data["browser_session_id"])
            
            # Remove from user sessions
            user_id = session_data["user_id"]
            if user_id in self.user_sessions:
                self.user_sessions[user_id] = [
                    sid for sid in self.user_sessions[user_id] if sid != session_id
                ]
                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]
            
            # Remove from account sessions
            account_id = session_data["account_id"]
            if account_id in self.account_sessions:
                del self.account_sessions[account_id]
            
            # Remove session data
            del self.active_sessions[session_id]
            
            # Remove session file
            self._delete_session_file(session_id)
            
            return True
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if current_time > session_data["expires_at"]:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.close_session(session_id)
    
    def _save_session(self, session_id: str):
        """Save session data to disk"""
        if session_id not in self.active_sessions:
            return
        
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        session_data = self.active_sessions[session_id].copy()
        
        # Convert datetime objects to ISO strings for JSON serialization
        session_data["created_at"] = session_data["created_at"].isoformat()
        session_data["last_activity"] = session_data["last_activity"].isoformat()
        session_data["expires_at"] = session_data["expires_at"].isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def _delete_session_file(self, session_id: str):
        """Delete session file from disk"""
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        if os.path.exists(session_file):
            os.remove(session_file)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_sessions = len(self.active_sessions)
        active_sessions = sum(1 for sid in self.active_sessions if self.is_session_active(sid))
        
        platform_stats = {}
        session_type_stats = {}
        
        for session_data in self.active_sessions.values():
            platform = session_data["platform"]
            session_type = session_data["session_type"]
            
            platform_stats[platform] = platform_stats.get(platform, 0) + 1
            session_type_stats[session_type] = session_type_stats.get(session_type, 0) + 1
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": total_sessions - active_sessions,
            "platform_distribution": platform_stats,
            "session_type_distribution": session_type_stats,
            "total_users": len(self.user_sessions)
        }


# Global session manager instance
session_manager = SessionManager()

