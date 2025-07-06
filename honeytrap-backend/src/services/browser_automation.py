"""
Browser Automation Service
Handles complex authentication flows using browser automation
"""

import os
import json
import time
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc


class BrowserAutomationService:
    """Service for automating browser-based authentication"""
    
    def __init__(self):
        self.drivers = {}  # Store active browser sessions
        self.session_data = {}  # Store session cookies and data
        self.profiles_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'browser_profiles')
        os.makedirs(self.profiles_dir, exist_ok=True)
    
    def create_browser_session(self, account_id: str, platform: str, headless: bool = True) -> str:
        """Create a new browser session for an account"""
        session_id = f"{account_id}_{platform}_{int(time.time())}"
        
        # Configure Chrome options
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Use profile directory for persistent sessions
        profile_dir = os.path.join(self.profiles_dir, account_id)
        os.makedirs(profile_dir, exist_ok=True)
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        
        try:
            # Use undetected-chromedriver to avoid detection
            driver = uc.Chrome(options=chrome_options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.drivers[session_id] = {
                "driver": driver,
                "account_id": account_id,
                "platform": platform,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            return session_id
            
        except Exception as e:
            raise Exception(f"Failed to create browser session: {e}")
    
    def login_facebook(self, session_id: str, username: str, password: str) -> Dict[str, Any]:
        """Login to Facebook using browser automation"""
        if session_id not in self.drivers:
            raise ValueError("Invalid session ID")
        
        driver = self.drivers[session_id]["driver"]
        
        try:
            # Navigate to Facebook login
            driver.get("https://www.facebook.com/login")
            
            # Wait for login form
            wait = WebDriverWait(driver, 10)
            
            # Find and fill username
            email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
            email_field.clear()
            email_field.send_keys(username)
            
            # Find and fill password
            password_field = driver.find_element(By.ID, "pass")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = driver.find_element(By.NAME, "login")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            current_url = driver.current_url
            if "facebook.com" in current_url and "login" not in current_url:
                # Save session cookies
                cookies = driver.get_cookies()
                self._save_session_data(session_id, "facebook", cookies)
                
                return {
                    "success": True,
                    "platform": "facebook",
                    "username": username,
                    "session_id": session_id,
                    "cookies_saved": len(cookies)
                }
            else:
                # Check for error messages
                error_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='royal_login_form'] div[role='alert']")
                error_message = error_elements[0].text if error_elements else "Login failed"
                
                return {
                    "success": False,
                    "platform": "facebook",
                    "error": error_message
                }
                
        except TimeoutException:
            return {
                "success": False,
                "platform": "facebook",
                "error": "Login form not found or timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "platform": "facebook",
                "error": f"Login error: {str(e)}"
            }
    
    def login_instagram(self, session_id: str, username: str, password: str) -> Dict[str, Any]:
        """Login to Instagram using browser automation"""
        if session_id not in self.drivers:
            raise ValueError("Invalid session ID")
        
        driver = self.drivers[session_id]["driver"]
        
        try:
            # Navigate to Instagram login
            driver.get("https://www.instagram.com/accounts/login/")
            
            # Wait for login form
            wait = WebDriverWait(driver, 10)
            
            # Find and fill username
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and fill password
            password_field = driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            current_url = driver.current_url
            if "instagram.com" in current_url and "login" not in current_url:
                # Handle "Save Login Info" prompt if it appears
                try:
                    not_now_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                    )
                    not_now_button.click()
                except TimeoutException:
                    pass
                
                # Handle "Turn on Notifications" prompt if it appears
                try:
                    not_now_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                    )
                    not_now_button.click()
                except TimeoutException:
                    pass
                
                # Save session cookies
                cookies = driver.get_cookies()
                self._save_session_data(session_id, "instagram", cookies)
                
                return {
                    "success": True,
                    "platform": "instagram",
                    "username": username,
                    "session_id": session_id,
                    "cookies_saved": len(cookies)
                }
            else:
                # Check for error messages
                error_elements = driver.find_elements(By.CSS_SELECTOR, "#slfErrorAlert")
                error_message = error_elements[0].text if error_elements else "Login failed"
                
                return {
                    "success": False,
                    "platform": "instagram",
                    "error": error_message
                }
                
        except TimeoutException:
            return {
                "success": False,
                "platform": "instagram",
                "error": "Login form not found or timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "platform": "instagram",
                "error": f"Login error: {str(e)}"
            }
    
    def login_tiktok(self, session_id: str, username: str, password: str) -> Dict[str, Any]:
        """Login to TikTok using browser automation"""
        if session_id not in self.drivers:
            raise ValueError("Invalid session ID")
        
        driver = self.drivers[session_id]["driver"]
        
        try:
            # Navigate to TikTok login
            driver.get("https://www.tiktok.com/login")
            
            # Wait for login options
            wait = WebDriverWait(driver, 10)
            
            # Click on "Use phone / email / username"
            email_login_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(), 'Use phone / email / username')]")
            ))
            email_login_button.click()
            
            time.sleep(2)
            
            # Find and fill username/email
            username_field = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Email or username']")
            ))
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and fill password
            password_field = driver.find_element(By.XPATH, "//input[@type='password']")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = driver.find_element(By.XPATH, "//button[@data-e2e='login-button']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(10)  # TikTok may have additional verification steps
            
            # Check if login was successful
            current_url = driver.current_url
            if "tiktok.com" in current_url and "login" not in current_url:
                # Save session cookies
                cookies = driver.get_cookies()
                self._save_session_data(session_id, "tiktok", cookies)
                
                return {
                    "success": True,
                    "platform": "tiktok",
                    "username": username,
                    "session_id": session_id,
                    "cookies_saved": len(cookies)
                }
            else:
                return {
                    "success": False,
                    "platform": "tiktok",
                    "error": "Login failed or additional verification required"
                }
                
        except TimeoutException:
            return {
                "success": False,
                "platform": "tiktok",
                "error": "Login form not found or timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "platform": "tiktok",
                "error": f"Login error: {str(e)}"
            }
    
    def login_snapchat(self, session_id: str, username: str, password: str) -> Dict[str, Any]:
        """Login to Snapchat using browser automation"""
        if session_id not in self.drivers:
            raise ValueError("Invalid session ID")
        
        driver = self.drivers[session_id]["driver"]
        
        try:
            # Navigate to Snapchat web
            driver.get("https://web.snapchat.com/")
            
            # Wait for login form
            wait = WebDriverWait(driver, 10)
            
            # Find and fill username
            username_field = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@data-testid='username']")
            ))
            username_field.clear()
            username_field.send_keys(username)
            
            # Find and fill password
            password_field = driver.find_element(By.XPATH, "//input[@data-testid='password']")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = driver.find_element(By.XPATH, "//button[@data-testid='login-submit-button']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(10)
            
            # Check if login was successful
            current_url = driver.current_url
            if "web.snapchat.com" in current_url and "login" not in current_url:
                # Save session cookies
                cookies = driver.get_cookies()
                self._save_session_data(session_id, "snapchat", cookies)
                
                return {
                    "success": True,
                    "platform": "snapchat",
                    "username": username,
                    "session_id": session_id,
                    "cookies_saved": len(cookies)
                }
            else:
                return {
                    "success": False,
                    "platform": "snapchat",
                    "error": "Login failed or additional verification required"
                }
                
        except TimeoutException:
            return {
                "success": False,
                "platform": "snapchat",
                "error": "Login form not found or timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "platform": "snapchat",
                "error": f"Login error: {str(e)}"
            }
    
    def _save_session_data(self, session_id: str, platform: str, cookies: List[Dict]):
        """Save session cookies and data"""
        session_file = os.path.join(self.profiles_dir, f"{session_id}_session.json")
        
        session_data = {
            "session_id": session_id,
            "platform": platform,
            "cookies": cookies,
            "saved_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        self.session_data[session_id] = session_data
    
    def load_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load saved session data"""
        session_file = os.path.join(self.profiles_dir, f"{session_id}_session.json")
        
        if os.path.exists(session_file):
            with open(session_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def restore_session(self, session_id: str, platform: str) -> bool:
        """Restore a saved browser session"""
        if session_id not in self.drivers:
            return False
        
        session_data = self.load_session_data(session_id)
        if not session_data:
            return False
        
        driver = self.drivers[session_id]["driver"]
        
        try:
            # Navigate to platform
            platform_urls = {
                "facebook": "https://www.facebook.com",
                "instagram": "https://www.instagram.com",
                "tiktok": "https://www.tiktok.com",
                "snapchat": "https://web.snapchat.com"
            }
            
            if platform in platform_urls:
                driver.get(platform_urls[platform])
                
                # Add saved cookies
                for cookie in session_data["cookies"]:
                    try:
                        driver.add_cookie(cookie)
                    except Exception:
                        pass  # Some cookies might not be valid anymore
                
                # Refresh page to apply cookies
                driver.refresh()
                time.sleep(3)
                
                return True
        
        except Exception as e:
            print(f"Error restoring session: {e}")
        
        return False
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of a browser session"""
        if session_id not in self.drivers:
            return {"active": False, "error": "Session not found"}
        
        session = self.drivers[session_id]
        driver = session["driver"]
        
        try:
            # Check if driver is still responsive
            current_url = driver.current_url
            
            return {
                "active": True,
                "session_id": session_id,
                "account_id": session["account_id"],
                "platform": session["platform"],
                "current_url": current_url,
                "created_at": session["created_at"].isoformat(),
                "last_activity": session["last_activity"].isoformat()
            }
        
        except Exception as e:
            return {
                "active": False,
                "session_id": session_id,
                "error": str(e)
            }
    
    def close_session(self, session_id: str) -> bool:
        """Close a browser session"""
        if session_id not in self.drivers:
            return False
        
        try:
            driver = self.drivers[session_id]["driver"]
            driver.quit()
            del self.drivers[session_id]
            return True
        
        except Exception as e:
            print(f"Error closing session {session_id}: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """Clean up expired browser sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.drivers.items():
            # Sessions expire after 2 hours of inactivity
            if (current_time - session["last_activity"]).total_seconds() > 7200:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.close_session(session_id)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get list of active browser sessions"""
        sessions = []
        
        for session_id in list(self.drivers.keys()):
            status = self.get_session_status(session_id)
            if status.get("active"):
                sessions.append(status)
            else:
                # Clean up inactive sessions
                self.close_session(session_id)
        
        return sessions


# Global browser automation service
browser_service = BrowserAutomationService()

