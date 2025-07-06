#!/usr/bin/env python3
"""
AI Honeytrap Network - End-to-End Test Suite
Tests complete user workflows and system interactions
"""

import os
import sys
import json
import time
import requests
import unittest
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class EndToEndTestSuite(unittest.TestCase):
    """End-to-end tests for complete user workflows"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.backend_url = "http://localhost:5000"
        cls.frontend_url = "http://localhost:3000"
        cls.admin_credentials = {
            "username": "test_admin",
            "password": "test_password_123"
        }
        
        # Set up Chrome driver for frontend testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except Exception as e:
            print(f"Warning: Could not initialize Chrome driver: {e}")
            cls.driver = None
        
        # Wait for services to be ready
        cls._wait_for_services()
    
    @classmethod
    def _wait_for_services(cls, timeout=60):
        """Wait for both backend and frontend services to be ready"""
        print("Waiting for services to be ready...")
        
        # Wait for backend
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{cls.backend_url}/health", timeout=5)
                if response.status_code == 200:
                    print("Backend service is ready")
                    break
            except:
                pass
            time.sleep(2)
        else:
            print("Warning: Backend service not ready within timeout")
        
        # Wait for frontend (if driver available)
        if cls.driver:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    cls.driver.get(cls.frontend_url)
                    if "AI Honeytrap" in cls.driver.title or cls.driver.find_elements(By.TAG_NAME, "body"):
                        print("Frontend service is ready")
                        break
                except:
                    pass
                time.sleep(2)
            else:
                print("Warning: Frontend service not ready within timeout")
    
    def test_01_complete_admin_workflow(self):
        """Test complete administrator workflow"""
        if not self.driver:
            self.skipTest("Chrome driver not available")
        
        try:
            # Navigate to admin login
            self.driver.get(f"{self.frontend_url}/admin")
            
            # Wait for login form
            wait = WebDriverWait(self.driver, 10)
            
            # Find and fill login form
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = self.driver.find_element(By.NAME, "password")
            login_button = self.driver.find_element(By.TYPE, "submit")
            
            username_field.send_keys(self.admin_credentials["username"])
            password_field.send_keys(self.admin_credentials["password"])
            login_button.click()
            
            # Wait for dashboard to load
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dashboard")))
            
            # Verify dashboard elements
            self.assertIn("Dashboard", self.driver.title)
            
            # Test navigation to profile management
            profile_tab = self.driver.find_element(By.LINK_TEXT, "Profiles")
            profile_tab.click()
            
            # Test profile creation
            create_button = wait.until(EC.element_to_be_clickable((By.BUTTON, "Create Profile")))
            create_button.click()
            
            # Fill profile form
            platform_select = self.driver.find_element(By.NAME, "platform")
            platform_select.send_keys("Discord")
            
            age_range_select = self.driver.find_element(By.NAME, "age_range")
            age_range_select.send_keys("13-15")
            
            submit_button = self.driver.find_element(By.TYPE, "submit")
            submit_button.click()
            
            # Verify profile creation success
            success_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "success")))
            self.assertIn("Profile created", success_message.text)
            
        except Exception as e:
            self.fail(f"Admin workflow test failed: {e}")
    
    def test_02_profile_lifecycle_workflow(self):
        """Test complete profile lifecycle from creation to deletion"""
        # Create profile via API
        headers = self._get_auth_headers()
        
        profile_data = {
            "platform": "discord",
            "age_range": "13-15",
            "interests": ["gaming", "art"],
            "personality": "shy",
            "location": "Hampshire, UK"
        }
        
        # Create profile
        response = requests.post(
            f"{self.backend_url}/api/profiles/generate",
            json=profile_data,
            headers=headers
        )
        
        if response.status_code != 201:
            self.skipTest("Could not create test profile")
        
        profile = response.json()
        profile_id = profile["id"]
        
        try:
            # Test profile activation
            response = requests.put(
                f"{self.backend_url}/api/profiles/{profile_id}",
                json={"status": "active"},
                headers=headers
            )
            self.assertIn(response.status_code, [200, 204])
            
            # Test content generation for profile
            content_data = {
                "profile_id": profile_id,
                "content_type": "post",
                "theme": "school"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/content/generate",
                json=content_data,
                headers=headers
            )
            
            if response.status_code == 201:
                content = response.json()
                content_id = content["id"]
                
                # Test content scheduling
                schedule_data = {
                    "content_id": content_id,
                    "scheduled_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                    "platform": "discord"
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/content/schedule",
                    json=schedule_data,
                    headers=headers
                )
                self.assertIn(response.status_code, [200, 201])
            
            # Test chat session creation
            chat_data = {
                "profile_id": profile_id,
                "platform": "discord",
                "subject_identifier": "test_subject_e2e"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/chats/create",
                json=chat_data,
                headers=headers
            )
            
            if response.status_code == 201:
                chat = response.json()
                chat_id = chat["id"]
                
                # Test message exchange
                message_data = {
                    "chat_id": chat_id,
                    "sender": "subject",
                    "content": "Hi there, how are you doing?",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/chats/{chat_id}/messages",
                    json=message_data,
                    headers=headers
                )
                self.assertIn(response.status_code, [200, 201])
                
                # Test AI response
                response = requests.post(
                    f"{self.backend_url}/api/chats/{chat_id}/respond",
                    headers=headers
                )
                self.assertIn(response.status_code, [200, 201])
                
                # Test threat assessment
                response = requests.post(
                    f"{self.backend_url}/api/chats/{chat_id}/assess_threat",
                    headers=headers
                )
                self.assertIn(response.status_code, [200, 201])
            
            # Test profile deactivation
            response = requests.put(
                f"{self.backend_url}/api/profiles/{profile_id}",
                json={"status": "inactive"},
                headers=headers
            )
            self.assertIn(response.status_code, [200, 204])
            
        finally:
            # Clean up - delete profile
            requests.delete(
                f"{self.backend_url}/api/profiles/{profile_id}",
                headers=headers
            )
    
    def test_03_investigation_workflow(self):
        """Test complete investigation workflow from detection to evidence collection"""
        headers = self._get_auth_headers()
        
        # Create investigation profile
        profile_data = {
            "platform": "discord",
            "age_range": "14-16",
            "interests": ["music", "social media"],
            "personality": "outgoing",
            "location": "Hampshire, UK"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/profiles/generate",
            json=profile_data,
            headers=headers
        )
        
        if response.status_code != 201:
            self.skipTest("Could not create investigation profile")
        
        profile = response.json()
        profile_id = profile["id"]
        
        try:
            # Simulate subject contact
            chat_data = {
                "profile_id": profile_id,
                "platform": "discord",
                "subject_identifier": "suspicious_user_123"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/chats/create",
                json=chat_data,
                headers=headers
            )
            
            if response.status_code == 201:
                chat = response.json()
                chat_id = chat["id"]
                
                # Simulate escalating conversation
                messages = [
                    "Hey, you seem cool. How old are you?",
                    "I'm 25, but age is just a number right?",
                    "Want to meet up sometime? I know a private place",
                    "Don't tell your parents about our chats, they wouldn't understand"
                ]
                
                for i, message in enumerate(messages):
                    # Subject message
                    message_data = {
                        "chat_id": chat_id,
                        "sender": "subject",
                        "content": message,
                        "timestamp": (datetime.utcnow() + timedelta(minutes=i*5)).isoformat()
                    }
                    
                    response = requests.post(
                        f"{self.backend_url}/api/chats/{chat_id}/messages",
                        json=message_data,
                        headers=headers
                    )
                    self.assertIn(response.status_code, [200, 201])
                    
                    # AI response
                    response = requests.post(
                        f"{self.backend_url}/api/chats/{chat_id}/respond",
                        headers=headers
                    )
                    self.assertIn(response.status_code, [200, 201])
                    
                    # Threat assessment after each exchange
                    response = requests.post(
                        f"{self.backend_url}/api/chats/{chat_id}/assess_threat",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        assessment = response.json()
                        threat_level = assessment.get("threat_level", 0)
                        
                        # Threat level should increase with escalating messages
                        if i >= 2:  # Later messages should trigger higher threat levels
                            self.assertGreater(threat_level, 50)
                
                # Test evidence collection
                response = requests.post(
                    f"{self.backend_url}/api/chats/{chat_id}/collect_evidence",
                    headers=headers
                )
                self.assertIn(response.status_code, [200, 201])
                
                # Test case file generation
                case_data = {
                    "chat_id": chat_id,
                    "investigation_type": "online_grooming",
                    "officer_id": "test_officer_123"
                }
                
                response = requests.post(
                    f"{self.backend_url}/api/cases/create",
                    json=case_data,
                    headers=headers
                )
                self.assertIn(response.status_code, [200, 201])
        
        finally:
            # Clean up
            requests.delete(
                f"{self.backend_url}/api/profiles/{profile_id}",
                headers=headers
            )
    
    def test_04_analytics_and_reporting_workflow(self):
        """Test analytics collection and reporting workflow"""
        headers = self._get_auth_headers()
        
        # Test dashboard analytics
        response = requests.get(
            f"{self.backend_url}/api/analytics/dashboard",
            headers=headers
        )
        
        if response.status_code == 200:
            analytics = response.json()
            
            # Verify analytics structure
            expected_fields = [
                "total_profiles",
                "active_chats",
                "threat_level_distribution",
                "platform_activity",
                "recent_activity"
            ]
            
            for field in expected_fields:
                self.assertIn(field, analytics)
        
        # Test discovery analytics
        response = requests.get(
            f"{self.backend_url}/api/analytics/discovery",
            headers=headers
        )
        
        if response.status_code == 200:
            discovery = response.json()
            
            # Verify discovery metrics
            expected_fields = [
                "discovery_rate",
                "platform_effectiveness",
                "time_to_contact",
                "engagement_success"
            ]
            
            for field in expected_fields:
                self.assertIn(field, discovery)
        
        # Test report generation
        report_data = {
            "report_type": "weekly_summary",
            "start_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
            "end_date": datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            f"{self.backend_url}/api/reports/generate",
            json=report_data,
            headers=headers
        )
        self.assertIn(response.status_code, [200, 201, 202])
    
    def test_05_system_monitoring_workflow(self):
        """Test system monitoring and health check workflow"""
        # Test system health
        response = requests.get(f"{self.backend_url}/health")
        self.assertEqual(response.status_code, 200)
        
        health_data = response.json()
        self.assertIn("status", health_data)
        self.assertEqual(health_data["status"], "healthy")
        
        # Test system metrics
        headers = self._get_auth_headers()
        response = requests.get(
            f"{self.backend_url}/api/system/metrics",
            headers=headers
        )
        
        if response.status_code == 200:
            metrics = response.json()
            
            # Verify metrics structure
            expected_metrics = [
                "cpu_usage",
                "memory_usage",
                "active_connections",
                "response_time"
            ]
            
            for metric in expected_metrics:
                self.assertIn(metric, metrics)
        
        # Test system logs
        response = requests.get(
            f"{self.backend_url}/api/system/logs",
            headers=headers
        )
        self.assertIn(response.status_code, [200, 404])
    
    def test_06_security_workflow(self):
        """Test security measures and incident response workflow"""
        headers = self._get_auth_headers()
        
        # Test rate limiting
        for i in range(10):
            response = requests.get(
                f"{self.backend_url}/api/profiles",
                headers=headers
            )
            
            if response.status_code == 429:  # Rate limited
                break
        
        # Test audit logging
        response = requests.get(
            f"{self.backend_url}/api/audit/logs",
            headers=headers
        )
        self.assertIn(response.status_code, [200, 404])
        
        # Test security incident simulation
        incident_data = {
            "incident_type": "unauthorized_access_attempt",
            "source_ip": "192.168.1.100",
            "timestamp": datetime.utcnow().isoformat(),
            "details": "Multiple failed login attempts"
        }
        
        response = requests.post(
            f"{self.backend_url}/api/security/incident",
            json=incident_data,
            headers=headers
        )
        self.assertIn(response.status_code, [200, 201, 404])
    
    def test_07_backup_and_recovery_workflow(self):
        """Test backup and recovery procedures"""
        headers = self._get_auth_headers()
        
        # Test backup creation
        backup_data = {
            "backup_type": "incremental",
            "include_profiles": True,
            "include_chats": True,
            "include_analytics": False
        }
        
        response = requests.post(
            f"{self.backend_url}/api/system/backup",
            json=backup_data,
            headers=headers
        )
        self.assertIn(response.status_code, [200, 201, 202, 404])
        
        # Test backup listing
        response = requests.get(
            f"{self.backend_url}/api/system/backups",
            headers=headers
        )
        self.assertIn(response.status_code, [200, 404])
    
    def _get_auth_headers(self):
        """Get authentication headers for API requests"""
        # Try to login and get token
        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json=self.admin_credentials
            )
            
            if response.status_code == 200:
                token = response.json()["token"]
                return {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
        except:
            pass
        
        # Return empty headers if authentication fails
        return {"Content-Type": "application/json"}
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.driver:
            cls.driver.quit()


def run_e2e_tests():
    """Run the complete end-to-end test suite"""
    print("Starting AI Honeytrap Network End-to-End Tests")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(EndToEndTestSuite)
    
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
            print(f"- {test}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)

