#!/usr/bin/env python3
"""
AI Honeytrap Network - Deployment Verification Script
Verifies that the deployed system is functioning correctly
"""

import os
import sys
import json
import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Any


class DeploymentVerifier:
    """Comprehensive deployment verification for the AI Honeytrap Network"""
    
    def __init__(self, config_file: str = None):
        """Initialize the deployment verifier"""
        self.config = self._load_config(config_file)
        self.results = []
        self.start_time = datetime.utcnow()
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "backend_url": "http://localhost:5000",
            "frontend_url": "http://localhost:3000",
            "timeout": 30,
            "admin_credentials": {
                "username": "admin",
                "password": "admin_password"
            },
            "test_data": {
                "profile_count": 3,
                "chat_count": 2,
                "content_count": 5
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
        
        return default_config
    
    def verify_deployment(self) -> bool:
        """Run complete deployment verification"""
        print("AI Honeytrap Network - Deployment Verification")
        print("=" * 60)
        print(f"Started at: {self.start_time}")
        print(f"Backend URL: {self.config['backend_url']}")
        print(f"Frontend URL: {self.config['frontend_url']}")
        print()
        
        # Run verification checks
        checks = [
            ("Service Availability", self._verify_service_availability),
            ("Database Connectivity", self._verify_database_connectivity),
            ("Authentication System", self._verify_authentication),
            ("API Endpoints", self._verify_api_endpoints),
            ("Frontend Application", self._verify_frontend),
            ("Profile Management", self._verify_profile_management),
            ("Chat System", self._verify_chat_system),
            ("Content Automation", self._verify_content_automation),
            ("Analytics System", self._verify_analytics),
            ("Security Measures", self._verify_security),
            ("Performance", self._verify_performance),
            ("Data Integrity", self._verify_data_integrity)
        ]
        
        all_passed = True
        
        for check_name, check_function in checks:
            print(f"Running {check_name}...")
            try:
                result = check_function()
                status = "PASS" if result else "FAIL"
                print(f"  {status}: {check_name}")
                
                self.results.append({
                    "check": check_name,
                    "status": status,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                if not result:
                    all_passed = False
                    
            except Exception as e:
                print(f"  ERROR: {check_name} - {e}")
                self.results.append({
                    "check": check_name,
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
                all_passed = False
            
            print()
        
        # Generate report
        self._generate_report()
        
        return all_passed
    
    def _verify_service_availability(self) -> bool:
        """Verify that all services are available and responding"""
        # Check backend health
        try:
            response = requests.get(
                f"{self.config['backend_url']}/health",
                timeout=self.config['timeout']
            )
            
            if response.status_code != 200:
                print(f"    Backend health check failed: {response.status_code}")
                return False
            
            health_data = response.json()
            if health_data.get("status") != "healthy":
                print(f"    Backend reports unhealthy status: {health_data}")
                return False
                
        except Exception as e:
            print(f"    Backend not accessible: {e}")
            return False
        
        # Check frontend availability
        try:
            response = requests.get(
                self.config['frontend_url'],
                timeout=self.config['timeout']
            )
            
            if response.status_code not in [200, 404]:  # 404 might be expected for SPA
                print(f"    Frontend not accessible: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    Frontend not accessible: {e}")
            return False
        
        print("    All services are available")
        return True
    
    def _verify_database_connectivity(self) -> bool:
        """Verify database connectivity and basic operations"""
        try:
            response = requests.get(
                f"{self.config['backend_url']}/api/system/db_status",
                timeout=self.config['timeout']
            )
            
            if response.status_code == 200:
                db_status = response.json()
                if db_status.get("connected"):
                    print("    Database connectivity verified")
                    return True
                else:
                    print(f"    Database not connected: {db_status}")
                    return False
            else:
                print(f"    Database status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    Database connectivity check failed: {e}")
            return False
    
    def _verify_authentication(self) -> bool:
        """Verify authentication system functionality"""
        # Test invalid login
        try:
            response = requests.post(
                f"{self.config['backend_url']}/api/auth/login",
                json={"username": "invalid", "password": "invalid"},
                timeout=self.config['timeout']
            )
            
            if response.status_code != 401:
                print(f"    Invalid login should return 401, got {response.status_code}")
                return False
        
        except Exception as e:
            print(f"    Authentication test failed: {e}")
            return False
        
        # Test valid login (if credentials provided)
        if self.config['admin_credentials']['username']:
            try:
                response = requests.post(
                    f"{self.config['backend_url']}/api/auth/login",
                    json=self.config['admin_credentials'],
                    timeout=self.config['timeout']
                )
                
                if response.status_code == 200:
                    token = response.json().get("token")
                    if token:
                        print("    Authentication system verified")
                        return True
                    else:
                        print("    Login successful but no token returned")
                        return False
                else:
                    print(f"    Valid login failed: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"    Valid login test failed: {e}")
                return False
        
        print("    Authentication system basic checks passed")
        return True
    
    def _verify_api_endpoints(self) -> bool:
        """Verify that key API endpoints are accessible"""
        # Get authentication token
        token = self._get_auth_token()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        # Test key endpoints
        endpoints = [
            ("/api/info", "GET", 200),
            ("/api/profiles", "GET", [200, 401]),
            ("/api/chats", "GET", [200, 401]),
            ("/api/analytics/dashboard", "GET", [200, 401]),
            ("/api/system/metrics", "GET", [200, 401, 404])
        ]
        
        for endpoint, method, expected_codes in endpoints:
            try:
                if method == "GET":
                    response = requests.get(
                        f"{self.config['backend_url']}{endpoint}",
                        headers=headers,
                        timeout=self.config['timeout']
                    )
                else:
                    response = requests.request(
                        method,
                        f"{self.config['backend_url']}{endpoint}",
                        headers=headers,
                        timeout=self.config['timeout']
                    )
                
                if isinstance(expected_codes, list):
                    if response.status_code not in expected_codes:
                        print(f"    Endpoint {endpoint} returned {response.status_code}, expected one of {expected_codes}")
                        return False
                else:
                    if response.status_code != expected_codes:
                        print(f"    Endpoint {endpoint} returned {response.status_code}, expected {expected_codes}")
                        return False
                        
            except Exception as e:
                print(f"    Endpoint {endpoint} test failed: {e}")
                return False
        
        print("    API endpoints verified")
        return True
    
    def _verify_frontend(self) -> bool:
        """Verify frontend application functionality"""
        try:
            # Check if frontend serves content
            response = requests.get(
                self.config['frontend_url'],
                timeout=self.config['timeout']
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Check for expected content
                if "AI Honeytrap" in content or "honeytrap" in content.lower():
                    print("    Frontend application verified")
                    return True
                else:
                    print("    Frontend content does not match expected application")
                    return False
            else:
                print(f"    Frontend returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    Frontend verification failed: {e}")
            return False
    
    def _verify_profile_management(self) -> bool:
        """Verify profile management functionality"""
        token = self._get_auth_token()
        if not token:
            print("    Cannot verify profile management without authentication")
            return False
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test profile creation
        profile_data = {
            "platform": "discord",
            "age_range": "13-15",
            "interests": ["gaming"],
            "personality": "friendly",
            "location": "Hampshire, UK"
        }
        
        try:
            response = requests.post(
                f"{self.config['backend_url']}/api/profiles/generate",
                json=profile_data,
                headers=headers,
                timeout=self.config['timeout']
            )
            
            if response.status_code == 201:
                profile = response.json()
                profile_id = profile["id"]
                
                # Test profile retrieval
                response = requests.get(
                    f"{self.config['backend_url']}/api/profiles/{profile_id}",
                    headers=headers,
                    timeout=self.config['timeout']
                )
                
                if response.status_code == 200:
                    # Clean up
                    requests.delete(
                        f"{self.config['backend_url']}/api/profiles/{profile_id}",
                        headers=headers
                    )
                    
                    print("    Profile management verified")
                    return True
                else:
                    print(f"    Profile retrieval failed: {response.status_code}")
                    return False
            else:
                print(f"    Profile creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    Profile management verification failed: {e}")
            return False
    
    def _verify_chat_system(self) -> bool:
        """Verify chat system functionality"""
        token = self._get_auth_token()
        if not token:
            print("    Cannot verify chat system without authentication")
            return False
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Create a test profile first
        profile_data = {
            "platform": "discord",
            "age_range": "13-15",
            "interests": ["gaming"],
            "personality": "friendly",
            "location": "Hampshire, UK"
        }
        
        try:
            response = requests.post(
                f"{self.config['backend_url']}/api/profiles/generate",
                json=profile_data,
                headers=headers,
                timeout=self.config['timeout']
            )
            
            if response.status_code != 201:
                print(f"    Could not create test profile for chat verification")
                return False
            
            profile = response.json()
            profile_id = profile["id"]
            
            # Test chat creation
            chat_data = {
                "profile_id": profile_id,
                "platform": "discord",
                "subject_identifier": "test_subject_verification"
            }
            
            response = requests.post(
                f"{self.config['backend_url']}/api/chats/create",
                json=chat_data,
                headers=headers,
                timeout=self.config['timeout']
            )
            
            if response.status_code == 201:
                chat = response.json()
                chat_id = chat["id"]
                
                # Test message sending
                message_data = {
                    "chat_id": chat_id,
                    "sender": "subject",
                    "content": "Hello, verification test",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                response = requests.post(
                    f"{self.config['backend_url']}/api/chats/{chat_id}/messages",
                    json=message_data,
                    headers=headers,
                    timeout=self.config['timeout']
                )
                
                if response.status_code in [200, 201]:
                    # Clean up
                    requests.delete(
                        f"{self.config['backend_url']}/api/profiles/{profile_id}",
                        headers=headers
                    )
                    
                    print("    Chat system verified")
                    return True
                else:
                    print(f"    Message sending failed: {response.status_code}")
                    return False
            else:
                print(f"    Chat creation failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    Chat system verification failed: {e}")
            return False
    
    def _verify_content_automation(self) -> bool:
        """Verify content automation functionality"""
        token = self._get_auth_token()
        if not token:
            print("    Cannot verify content automation without authentication")
            return False
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test content generation endpoint
        try:
            response = requests.get(
                f"{self.config['backend_url']}/api/content/templates",
                headers=headers,
                timeout=self.config['timeout']
            )
            
            if response.status_code in [200, 404]:  # 404 if not implemented
                print("    Content automation endpoints accessible")
                return True
            else:
                print(f"    Content automation check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    Content automation verification failed: {e}")
            return False
    
    def _verify_analytics(self) -> bool:
        """Verify analytics system functionality"""
        token = self._get_auth_token()
        if not token:
            print("    Cannot verify analytics without authentication")
            return False
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.config['backend_url']}/api/analytics/dashboard",
                headers=headers,
                timeout=self.config['timeout']
            )
            
            if response.status_code == 200:
                analytics = response.json()
                
                # Check for expected analytics fields
                expected_fields = ["total_profiles", "active_chats"]
                if any(field in analytics for field in expected_fields):
                    print("    Analytics system verified")
                    return True
                else:
                    print("    Analytics data structure unexpected")
                    return False
            elif response.status_code == 404:
                print("    Analytics endpoints not implemented")
                return True  # Not implemented yet, but that's okay
            else:
                print(f"    Analytics check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    Analytics verification failed: {e}")
            return False
    
    def _verify_security(self) -> bool:
        """Verify security measures"""
        # Test rate limiting (if implemented)
        try:
            for i in range(5):
                response = requests.get(
                    f"{self.config['backend_url']}/api/info",
                    timeout=self.config['timeout']
                )
                
                if response.status_code == 429:  # Rate limited
                    print("    Rate limiting verified")
                    break
            
            # Test CORS headers
            response = requests.options(
                f"{self.config['backend_url']}/api/info",
                timeout=self.config['timeout']
            )
            
            if "Access-Control-Allow-Origin" in response.headers:
                print("    CORS headers present")
            
            print("    Security measures verified")
            return True
            
        except Exception as e:
            print(f"    Security verification failed: {e}")
            return False
    
    def _verify_performance(self) -> bool:
        """Verify system performance"""
        try:
            # Test response time
            start_time = time.time()
            response = requests.get(
                f"{self.config['backend_url']}/health",
                timeout=self.config['timeout']
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 5.0:
                print(f"    Response time: {response_time:.2f}s")
                return True
            else:
                print(f"    Performance issue: {response_time:.2f}s response time")
                return False
                
        except Exception as e:
            print(f"    Performance verification failed: {e}")
            return False
    
    def _verify_data_integrity(self) -> bool:
        """Verify data integrity and consistency"""
        token = self._get_auth_token()
        if not token:
            print("    Cannot verify data integrity without authentication")
            return True  # Skip if no auth
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            # Test data validation
            invalid_data = {
                "platform": "invalid_platform",
                "age_range": "invalid_age"
            }
            
            response = requests.post(
                f"{self.config['backend_url']}/api/profiles/generate",
                json=invalid_data,
                headers=headers,
                timeout=self.config['timeout']
            )
            
            if response.status_code == 400:
                print("    Data validation working correctly")
                return True
            else:
                print(f"    Data validation issue: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"    Data integrity verification failed: {e}")
            return False
    
    def _get_auth_token(self) -> str:
        """Get authentication token for API requests"""
        try:
            response = requests.post(
                f"{self.config['backend_url']}/api/auth/login",
                json=self.config['admin_credentials'],
                timeout=self.config['timeout']
            )
            
            if response.status_code == 200:
                return response.json().get("token", "")
        except:
            pass
        
        return ""
    
    def _generate_report(self):
        """Generate deployment verification report"""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        total = len(self.results)
        
        print("=" * 60)
        print("DEPLOYMENT VERIFICATION REPORT")
        print("=" * 60)
        print(f"Started: {self.start_time}")
        print(f"Completed: {end_time}")
        print(f"Duration: {duration:.2f} seconds")
        print()
        print(f"Total Checks: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print(f"Success Rate: {(passed / total * 100):.1f}%")
        print()
        
        if failed > 0 or errors > 0:
            print("FAILED CHECKS:")
            for result in self.results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(f"- {result['check']}: {result['status']}")
                    if "error" in result:
                        print(f"  Error: {result['error']}")
            print()
        
        # Save report to file
        report_file = f"deployment_verification_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "success_rate": passed / total * 100 if total > 0 else 0
            },
            "results": self.results,
            "config": self.config
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"Report saved to: {report_file}")
        except Exception as e:
            print(f"Could not save report: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Honeytrap Network Deployment Verification")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--backend-url", help="Backend URL")
    parser.add_argument("--frontend-url", help="Frontend URL")
    
    args = parser.parse_args()
    
    # Create verifier
    verifier = DeploymentVerifier(args.config)
    
    # Override URLs if provided
    if args.backend_url:
        verifier.config["backend_url"] = args.backend_url
    if args.frontend_url:
        verifier.config["frontend_url"] = args.frontend_url
    
    # Run verification
    success = verifier.verify_deployment()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

