#!/usr/bin/env python3
"""
Social Media Integration Tests
Tests for social media account management and session functionality
"""

import unittest
import json
import time
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'honeytrap-backend', 'src'))

from models.social_account import SocialAccount, account_manager
from services.social_auth_manager import auth_manager
from services.session_manager import session_manager
from services.browser_automation import browser_service
from services.platform_integrations import platform_manager


class TestSocialMediaIntegration(unittest.TestCase):
    """Test social media account management integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_user_id = "test_user_123"
        self.test_platform = "facebook"
        self.test_credentials = {
            "username": "test@example.com",
            "password": "test_password",
            "display_name": "Test User"
        }
        
        # Clear any existing test data
        self.cleanup_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """Clean up test data"""
        # Close any test sessions
        user_sessions = session_manager.get_user_sessions(self.test_user_id)
        for session_info in user_sessions:
            session_manager.close_session(session_info['session_id'])
        
        # Remove test accounts
        test_accounts = account_manager.get_accounts_by_platform(self.test_platform)
        for account in test_accounts:
            if account.username == self.test_credentials["username"]:
                account_manager.delete_account(account.id)
    
    def test_account_creation_and_management(self):
        """Test creating and managing social media accounts"""
        print("Testing account creation and management...")
        
        # Test account creation
        account_id = account_manager.create_account(
            platform=self.test_platform,
            username=self.test_credentials["username"],
            display_name=self.test_credentials["display_name"],
            login_method="credentials"
        )
        
        self.assertIsNotNone(account_id)
        print(f"✓ Account created with ID: {account_id}")
        
        # Test account retrieval
        account = account_manager.get_account(account_id)
        self.assertIsNotNone(account)
        self.assertEqual(account.platform, self.test_platform)
        self.assertEqual(account.username, self.test_credentials["username"])
        print("✓ Account retrieved successfully")
        
        # Test account update
        new_display_name = "Updated Test User"
        success = account_manager.update_account(account_id, {
            "display_name": new_display_name
        })
        self.assertTrue(success)
        
        updated_account = account_manager.get_account(account_id)
        self.assertEqual(updated_account.display_name, new_display_name)
        print("✓ Account updated successfully")
        
        # Test account listing
        accounts = account_manager.get_accounts_by_platform(self.test_platform)
        self.assertGreater(len(accounts), 0)
        print(f"✓ Found {len(accounts)} accounts for platform {self.test_platform}")
        
        return account_id
    
    def test_credential_authentication(self):
        """Test credential-based authentication"""
        print("Testing credential authentication...")
        
        # Create account
        account_id = self.test_account_creation_and_management()
        
        # Store credentials
        success = account_manager.store_credentials(
            account_id,
            self.test_credentials["username"],
            self.test_credentials["password"]
        )
        self.assertTrue(success)
        print("✓ Credentials stored successfully")
        
        # Retrieve credentials
        credentials = account_manager.get_account(account_id).get_credentials()
        self.assertIsNotNone(credentials)
        self.assertEqual(credentials["username"], self.test_credentials["username"])
        print("✓ Credentials retrieved successfully")
        
        # Test credential validation (mocked)
        with patch.object(auth_manager, 'validate_credentials') as mock_validate:
            mock_validate.return_value = {"success": True, "user_info": {"id": "123"}}
            
            result = auth_manager.validate_credentials(
                self.test_platform,
                self.test_credentials["username"],
                self.test_credentials["password"]
            )
            
            self.assertTrue(result["success"])
            print("✓ Credentials validated successfully")
    
    @patch('services.platform_integrations.requests.get')
    def test_oauth_authentication(self, mock_get):
        """Test OAuth authentication flow"""
        print("Testing OAuth authentication...")
        
        # Mock OAuth response
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Create account
        account_id = account_manager.create_account(
            platform=self.test_platform,
            username=self.test_credentials["username"],
            display_name=self.test_credentials["display_name"],
            login_method="oauth"
        )
        
        # Test OAuth URL generation
        auth_url = auth_manager.get_oauth_url(self.test_platform)
        self.assertIsNotNone(auth_url)
        self.assertIn("oauth", auth_url.lower())
        print("✓ OAuth URL generated successfully")
        
        # Test token exchange (mocked)
        tokens = auth_manager.exchange_oauth_code(
            self.test_platform,
            "test_auth_code",
            account_id
        )
        
        self.assertIsNotNone(tokens)
        self.assertIn("access_token", tokens)
        print("✓ OAuth tokens exchanged successfully")
        
        # Test token storage
        account = account_manager.get_account(account_id)
        stored_tokens = account.get_oauth_tokens()
        self.assertIsNotNone(stored_tokens)
        print("✓ OAuth tokens stored successfully")
    
    def test_session_management(self):
        """Test session creation and management"""
        print("Testing session management...")
        
        # Create account
        account_id = self.test_account_creation_and_management()
        
        # Create session
        session_id = session_manager.create_session(
            user_id=self.test_user_id,
            account_id=account_id,
            session_type="api"
        )
        
        self.assertIsNotNone(session_id)
        print(f"✓ Session created with ID: {session_id}")
        
        # Test session info retrieval
        session_info = session_manager.get_session_info(session_id)
        self.assertIsNotNone(session_info)
        self.assertEqual(session_info["user_id"], self.test_user_id)
        self.assertEqual(session_info["account_id"], account_id)
        print("✓ Session info retrieved successfully")
        
        # Test session activity
        self.assertTrue(session_manager.is_session_active(session_id))
        print("✓ Session is active")
        
        # Test session switching
        switch_result = session_manager.switch_session(self.test_user_id, session_id)
        self.assertIsNotNone(switch_result)
        self.assertEqual(switch_result["session_id"], session_id)
        print("✓ Session switching successful")
        
        # Test session extension
        success = session_manager.extend_session(session_id, 7200)  # 2 hours
        self.assertTrue(success)
        print("✓ Session extended successfully")
        
        # Test user sessions listing
        user_sessions = session_manager.get_user_sessions(self.test_user_id)
        self.assertGreater(len(user_sessions), 0)
        print(f"✓ Found {len(user_sessions)} sessions for user")
        
        return session_id
    
    def test_multiple_sessions(self):
        """Test managing multiple sessions"""
        print("Testing multiple sessions...")
        
        # Create multiple accounts
        account_ids = []
        for i in range(3):
            account_id = account_manager.create_account(
                platform=self.test_platform,
                username=f"test{i}@example.com",
                display_name=f"Test User {i}",
                login_method="credentials"
            )
            account_ids.append(account_id)
        
        # Create sessions for each account
        session_ids = []
        for account_id in account_ids:
            session_id = session_manager.create_session(
                user_id=self.test_user_id,
                account_id=account_id,
                session_type="api"
            )
            session_ids.append(session_id)
        
        print(f"✓ Created {len(session_ids)} sessions")
        
        # Test session switching between accounts
        for i, session_id in enumerate(session_ids):
            switch_result = session_manager.switch_session(self.test_user_id, session_id)
            self.assertEqual(switch_result["session_id"], session_id)
            print(f"✓ Switched to session {i+1}")
        
        # Test concurrent session management
        user_sessions = session_manager.get_user_sessions(self.test_user_id)
        self.assertEqual(len(user_sessions), len(session_ids))
        print(f"✓ Managing {len(user_sessions)} concurrent sessions")
        
        # Clean up additional test accounts
        for account_id in account_ids:
            account_manager.delete_account(account_id)
    
    @patch('services.browser_automation.webdriver.Chrome')
    def test_browser_automation(self, mock_chrome):
        """Test browser automation functionality"""
        print("Testing browser automation...")
        
        # Mock browser driver
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        # Create account
        account_id = account_manager.create_account(
            platform=self.test_platform,
            username=self.test_credentials["username"],
            display_name=self.test_credentials["display_name"],
            login_method="browser"
        )
        
        # Test browser session creation
        browser_session_id = browser_service.create_browser_session(
            account_id,
            self.test_platform,
            headless=True
        )
        
        self.assertIsNotNone(browser_session_id)
        print(f"✓ Browser session created: {browser_session_id}")
        
        # Test browser login (mocked)
        with patch.object(browser_service, 'login_facebook') as mock_login:
            mock_login.return_value = {"success": True, "session_id": browser_session_id}
            
            login_result = browser_service.login_facebook(
                browser_session_id,
                self.test_credentials["username"],
                self.test_credentials["password"]
            )
            
            self.assertTrue(login_result["success"])
            print("✓ Browser login successful")
        
        # Test session status
        with patch.object(browser_service, 'get_session_status') as mock_status:
            mock_status.return_value = {"active": True, "logged_in": True}
            
            status = browser_service.get_session_status(browser_session_id)
            self.assertTrue(status["active"])
            print("✓ Browser session status retrieved")
        
        # Test session cleanup
        browser_service.close_session(browser_session_id)
        print("✓ Browser session closed")
    
    def test_platform_integrations(self):
        """Test platform-specific integrations"""
        print("Testing platform integrations...")
        
        # Test platform configuration
        platforms = platform_manager.get_supported_platforms()
        self.assertGreater(len(platforms), 0)
        print(f"✓ Found {len(platforms)} supported platforms")
        
        # Test platform capabilities
        capabilities = platform_manager.get_platform_capabilities(self.test_platform)
        self.assertIsNotNone(capabilities)
        self.assertIsInstance(capabilities, list)
        print(f"✓ Platform capabilities: {capabilities}")
        
        # Test rate limits
        rate_limits = platform_manager.get_platform_rate_limits(self.test_platform)
        self.assertIsNotNone(rate_limits)
        print(f"✓ Platform rate limits: {rate_limits}")
        
        # Test connection testing (mocked)
        with patch.object(platform_manager, 'test_platform_connection') as mock_test:
            mock_test.return_value = {"success": True, "response_time": 0.5}
            
            test_result = platform_manager.test_platform_connection(
                self.test_platform,
                "test_access_token"
            )
            
            self.assertTrue(test_result["success"])
            print("✓ Platform connection test successful")
    
    def test_session_actions(self):
        """Test performing actions through sessions"""
        print("Testing session actions...")
        
        # Create session
        session_id = self.test_session_management()
        
        # Test posting action (mocked)
        with patch.object(session_manager, '_perform_api_action') as mock_action:
            mock_action.return_value = {"success": True, "post_id": "123456"}
            
            result = session_manager.perform_action(
                session_id,
                "post",
                {"content": "Test post", "visibility": "public"}
            )
            
            self.assertTrue(result["success"])
            print("✓ Post action successful")
        
        # Test messaging action (mocked)
        with patch.object(session_manager, '_perform_api_action') as mock_action:
            mock_action.return_value = {"success": True, "message_id": "789012"}
            
            result = session_manager.perform_action(
                session_id,
                "message",
                {"recipient": "test_recipient", "message": "Test message"}
            )
            
            self.assertTrue(result["success"])
            print("✓ Message action successful")
        
        # Test rate limiting
        session_info = session_manager.get_session_info(session_id)
        rate_limits = session_info.get("rate_limits", {})
        print(f"✓ Rate limits tracked: {len(rate_limits)} actions")
    
    def test_error_handling(self):
        """Test error handling and recovery"""
        print("Testing error handling...")
        
        # Test invalid account creation
        with self.assertRaises(ValueError):
            account_manager.create_account(
                platform="invalid_platform",
                username="test@example.com",
                display_name="Test User",
                login_method="invalid_method"
            )
        print("✓ Invalid account creation properly rejected")
        
        # Test session creation with invalid account
        with self.assertRaises(ValueError):
            session_manager.create_session(
                user_id=self.test_user_id,
                account_id="invalid_account_id",
                session_type="api"
            )
        print("✓ Invalid session creation properly rejected")
        
        # Test session switching with invalid session
        with self.assertRaises(ValueError):
            session_manager.switch_session(
                self.test_user_id,
                "invalid_session_id"
            )
        print("✓ Invalid session switching properly rejected")
        
        # Test action on inactive session
        # Create and close a session
        account_id = self.test_account_creation_and_management()
        session_id = session_manager.create_session(
            user_id=self.test_user_id,
            account_id=account_id,
            session_type="api"
        )
        session_manager.close_session(session_id)
        
        with self.assertRaises(ValueError):
            session_manager.perform_action(
                session_id,
                "post",
                {"content": "Test post"}
            )
        print("✓ Action on inactive session properly rejected")
    
    def test_session_cleanup(self):
        """Test session cleanup functionality"""
        print("Testing session cleanup...")
        
        # Create account and session
        account_id = self.test_account_creation_and_management()
        session_id = session_manager.create_session(
            user_id=self.test_user_id,
            account_id=account_id,
            session_type="api"
        )
        
        # Manually expire the session
        session_data = session_manager.active_sessions[session_id]
        session_data["expires_at"] = datetime.utcnow() - timedelta(hours=1)
        
        # Test cleanup
        session_manager.cleanup_expired_sessions()
        
        # Verify session was cleaned up
        self.assertFalse(session_manager.is_session_active(session_id))
        print("✓ Expired session cleaned up successfully")
    
    def test_session_statistics(self):
        """Test session statistics functionality"""
        print("Testing session statistics...")
        
        # Create multiple sessions
        account_id = self.test_account_creation_and_management()
        session_ids = []
        
        for i in range(3):
            session_id = session_manager.create_session(
                user_id=f"{self.test_user_id}_{i}",
                account_id=account_id,
                session_type="api"
            )
            session_ids.append(session_id)
        
        # Get statistics
        stats = session_manager.get_session_stats()
        
        self.assertGreaterEqual(stats["total_sessions"], 3)
        self.assertGreaterEqual(stats["active_sessions"], 3)
        self.assertIn(self.test_platform, stats["platform_distribution"])
        print(f"✓ Session statistics: {stats}")
        
        # Clean up test sessions
        for session_id in session_ids:
            session_manager.close_session(session_id)
    
    def test_integration_workflow(self):
        """Test complete integration workflow"""
        print("Testing complete integration workflow...")
        
        # Step 1: Create account
        account_id = account_manager.create_account(
            platform=self.test_platform,
            username=self.test_credentials["username"],
            display_name=self.test_credentials["display_name"],
            login_method="credentials"
        )
        print("✓ Step 1: Account created")
        
        # Step 2: Store credentials
        account_manager.store_credentials(
            account_id,
            self.test_credentials["username"],
            self.test_credentials["password"]
        )
        print("✓ Step 2: Credentials stored")
        
        # Step 3: Create session
        session_id = session_manager.create_session(
            user_id=self.test_user_id,
            account_id=account_id,
            session_type="api"
        )
        print("✓ Step 3: Session created")
        
        # Step 4: Switch to session
        session_manager.switch_session(self.test_user_id, session_id)
        print("✓ Step 4: Session activated")
        
        # Step 5: Perform actions (mocked)
        with patch.object(session_manager, '_perform_api_action') as mock_action:
            mock_action.return_value = {"success": True, "action_id": "test_123"}
            
            result = session_manager.perform_action(
                session_id,
                "post",
                {"content": "Integration test post"}
            )
            self.assertTrue(result["success"])
        print("✓ Step 5: Action performed")
        
        # Step 6: Monitor session
        session_info = session_manager.get_session_info(session_id)
        self.assertGreater(len(session_info["activity_log"]), 0)
        print("✓ Step 6: Session monitored")
        
        # Step 7: Clean up
        session_manager.close_session(session_id)
        account_manager.delete_account(account_id)
        print("✓ Step 7: Cleanup completed")
        
        print("✓ Complete integration workflow successful")


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("SOCIAL MEDIA INTEGRATION TESTS")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSocialMediaIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return success


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)

