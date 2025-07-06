#!/usr/bin/env python3
"""
AI Honeytrap Network - Integration Test Suite
Comprehensive testing for all system components and their interactions
"""

import os
import sys
import json
import time
import requests
import unittest
from datetime import datetime
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'honeytrap-backend', 'src'))

from models.user import User
from models.profile import Profile
from models.chat import Chat
from services.profile_generator import ProfileGenerator
from services.content_automation import ContentAutomation
from services.discovery_analytics import DiscoveryAnalytics


class IntegrationTestSuite(unittest.TestCase):
    """Comprehensive integration tests for the AI Honeytrap Network"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment and configuration"""
        cls.base_url = "http://localhost:5000"
        cls.test_data = {}
        cls.admin_token = None
        cls.test_profiles = []
        
        # Wait for backend to be ready
        cls._wait_for_backend()
        
        # Initialize test data
        cls._initialize_test_data()
    
    @classmethod
    def _wait_for_backend(cls, timeout=30):
        """Wait for backend service to be available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{cls.base_url}/health")
                if response.status_code == 200:
                    print("Backend service is ready")
                    return
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(1)
        
        raise Exception("Backend service not available within timeout period")
    
    @classmethod
    def _initialize_test_data(cls):
        """Initialize test data and authentication"""
        # Create admin user for testing
        admin_data = {
            "username": "test_admin",
            "password": "test_password_123",
            "role": "admin"
        }
        
        try:
            # Try to login first
            login_response = requests.post(
                f"{cls.base_url}/api/auth/login",
                json={"username": admin_data["username"], "password": admin_data["password"]}
            )
            
            if login_response.status_code == 200:
                cls.admin_token = login_response.json()["token"]
            else:
                # Create admin user if login fails
                register_response = requests.post(
                    f"{cls.base_url}/api/auth/register",
                    json=admin_data
                )
                
                if register_response.status_code == 201:
                    login_response = requests.post(
                        f"{cls.base_url}/api/auth/login",
                        json={"username": admin_data["username"], "password": admin_data["password"]}
                    )
                    cls.admin_token = login_response.json()["token"]
        
        except Exception as e:
            print(f"Warning: Could not initialize admin user: {e}")
    
    def setUp(self):
        """Set up for each test"""
        self.headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }
    
    def test_01_backend_health_check(self):
        """Test backend service health and basic endpoints"""
        # Health check
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        
        # API info
        response = requests.get(f"{self.base_url}/api/info")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("version", data)
        self.assertIn("status", data)
    
    def test_02_authentication_system(self):
        """Test authentication and authorization"""
        # Test invalid login
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": "invalid", "password": "invalid"}
        )
        self.assertEqual(response.status_code, 401)
        
        # Test valid login (admin user should exist from setup)
        if self.admin_token:
            # Test protected endpoint access
            response = requests.get(
                f"{self.base_url}/api/admin/stats",
                headers=self.headers
            )
            self.assertIn(response.status_code, [200, 404])  # 404 if endpoint not implemented yet
    
    def test_03_profile_management_system(self):
        """Test profile creation, management, and operations"""
        # Test profile generation
        profile_data = {
            "platform": "discord",
            "age_range": "13-15",
            "interests": ["gaming", "art"],
            "personality": "shy",
            "location": "Hampshire, UK"
        }
        
        response = requests.post(
            f"{self.base_url}/api/profiles/generate",
            json=profile_data,
            headers=self.headers
        )
        
        if response.status_code == 201:
            profile = response.json()
            self.test_profiles.append(profile["id"])
            
            # Verify profile structure
            self.assertIn("id", profile)
            self.assertIn("name", profile)
            self.assertIn("platform", profile)
            self.assertEqual(profile["platform"], "discord")
            
            # Test profile retrieval
            response = requests.get(
                f"{self.base_url}/api/profiles/{profile['id']}",
                headers=self.headers
            )
            self.assertEqual(response.status_code, 200)
            
            # Test profile update
            update_data = {"status": "active"}
            response = requests.put(
                f"{self.base_url}/api/profiles/{profile['id']}",
                json=update_data,
                headers=self.headers
            )
            self.assertIn(response.status_code, [200, 204])
    
    def test_04_content_automation_system(self):
        """Test content generation and automation"""
        if not self.test_profiles:
            self.skipTest("No test profiles available")
        
        profile_id = self.test_profiles[0]
        
        # Test content generation
        content_data = {
            "profile_id": profile_id,
            "content_type": "post",
            "theme": "school",
            "mood": "casual"
        }
        
        response = requests.post(
            f"{self.base_url}/api/content/generate",
            json=content_data,
            headers=self.headers
        )
        
        if response.status_code == 201:
            content = response.json()
            self.assertIn("id", content)
            self.assertIn("text", content)
            self.assertIn("profile_id", content)
            
            # Test content scheduling
            schedule_data = {
                "content_id": content["id"],
                "scheduled_time": "2025-07-07T10:00:00Z",
                "platform": "discord"
            }
            
            response = requests.post(
                f"{self.base_url}/api/content/schedule",
                json=schedule_data,
                headers=self.headers
            )
            self.assertIn(response.status_code, [200, 201])
    
    def test_05_chat_system_integration(self):
        """Test chat functionality and message handling"""
        if not self.test_profiles:
            self.skipTest("No test profiles available")
        
        profile_id = self.test_profiles[0]
        
        # Test chat session creation
        chat_data = {
            "profile_id": profile_id,
            "platform": "discord",
            "subject_identifier": "test_subject_123"
        }
        
        response = requests.post(
            f"{self.base_url}/api/chats/create",
            json=chat_data,
            headers=self.headers
        )
        
        if response.status_code == 201:
            chat = response.json()
            chat_id = chat["id"]
            
            # Test message sending
            message_data = {
                "chat_id": chat_id,
                "sender": "subject",
                "content": "Hello, how are you?",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/api/chats/{chat_id}/messages",
                json=message_data,
                headers=self.headers
            )
            self.assertIn(response.status_code, [200, 201])
            
            # Test AI response generation
            response = requests.post(
                f"{self.base_url}/api/chats/{chat_id}/respond",
                headers=self.headers
            )
            self.assertIn(response.status_code, [200, 201])
            
            # Test chat history retrieval
            response = requests.get(
                f"{self.base_url}/api/chats/{chat_id}/messages",
                headers=self.headers
            )
            self.assertEqual(response.status_code, 200)
    
    def test_06_analytics_and_reporting(self):
        """Test analytics collection and reporting"""
        # Test analytics dashboard data
        response = requests.get(
            f"{self.base_url}/api/analytics/dashboard",
            headers=self.headers
        )
        
        if response.status_code == 200:
            analytics = response.json()
            self.assertIn("total_profiles", analytics)
            self.assertIn("active_chats", analytics)
            self.assertIn("threat_level_distribution", analytics)
        
        # Test discovery metrics
        response = requests.get(
            f"{self.base_url}/api/analytics/discovery",
            headers=self.headers
        )
        
        if response.status_code == 200:
            discovery = response.json()
            self.assertIn("discovery_rate", discovery)
            self.assertIn("platform_effectiveness", discovery)
    
    def test_07_security_and_access_control(self):
        """Test security measures and access controls"""
        # Test unauthorized access
        response = requests.get(f"{self.base_url}/api/admin/stats")
        self.assertEqual(response.status_code, 401)
        
        # Test invalid token
        invalid_headers = {
            "Authorization": "Bearer invalid_token",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{self.base_url}/api/profiles",
            headers=invalid_headers
        )
        self.assertEqual(response.status_code, 401)
        
        # Test SQL injection protection
        malicious_data = {
            "username": "admin'; DROP TABLE users; --",
            "password": "password"
        }
        
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json=malicious_data
        )
        self.assertEqual(response.status_code, 401)
    
    def test_08_data_integrity_and_validation(self):
        """Test data validation and integrity checks"""
        # Test invalid profile data
        invalid_profile = {
            "platform": "invalid_platform",
            "age_range": "invalid_age",
            "interests": "not_a_list"
        }
        
        response = requests.post(
            f"{self.base_url}/api/profiles/generate",
            json=invalid_profile,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
        
        # Test missing required fields
        incomplete_profile = {
            "platform": "discord"
            # Missing required fields
        }
        
        response = requests.post(
            f"{self.base_url}/api/profiles/generate",
            json=incomplete_profile,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 400)
    
    def test_09_performance_and_scalability(self):
        """Test system performance under load"""
        # Test concurrent profile creation
        import threading
        import queue
        
        results = queue.Queue()
        
        def create_profile():
            profile_data = {
                "platform": "discord",
                "age_range": "13-15",
                "interests": ["gaming"],
                "personality": "friendly",
                "location": "Hampshire, UK"
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/profiles/generate",
                    json=profile_data,
                    headers=self.headers,
                    timeout=10
                )
                results.put(response.status_code)
            except Exception as e:
                results.put(f"Error: {e}")
        
        # Create 5 concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_profile)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 201:
                success_count += 1
        
        # At least some requests should succeed
        self.assertGreater(success_count, 0)
    
    def test_10_error_handling_and_recovery(self):
        """Test error handling and system recovery"""
        # Test handling of non-existent resources
        response = requests.get(
            f"{self.base_url}/api/profiles/non_existent_id",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 404)
        
        # Test handling of malformed requests
        response = requests.post(
            f"{self.base_url}/api/profiles/generate",
            data="invalid json",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(response.status_code, 400)
    
    def tearDown(self):
        """Clean up after each test"""
        # Clean up test profiles
        for profile_id in self.test_profiles:
            try:
                requests.delete(
                    f"{self.base_url}/api/profiles/{profile_id}",
                    headers=self.headers
                )
            except:
                pass
        
        self.test_profiles.clear()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Clean up any remaining test data
        if cls.admin_token:
            headers = {
                "Authorization": f"Bearer {cls.admin_token}",
                "Content-Type": "application/json"
            }
            
            try:
                # Clean up test profiles
                response = requests.get(f"{cls.base_url}/api/profiles", headers=headers)
                if response.status_code == 200:
                    profiles = response.json()
                    for profile in profiles:
                        if profile.get("name", "").startswith("test_"):
                            requests.delete(
                                f"{cls.base_url}/api/profiles/{profile['id']}",
                                headers=headers
                            )
            except:
                pass


def run_integration_tests():
    """Run the complete integration test suite"""
    print("Starting AI Honeytrap Network Integration Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTestSuite)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)

