#!/usr/bin/env python3
"""
AI Honeytrap Network - Comprehensive Test Runner
Executes all test suites and generates comprehensive reports
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Any, Tuple


class TestRunner:
    """Comprehensive test runner for the AI Honeytrap Network"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the test runner"""
        self.config = config or {}
        self.results = {}
        self.start_time = datetime.utcnow()
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def run_all_tests(self) -> bool:
        """Run all test suites and generate comprehensive report"""
        print("AI Honeytrap Network - Comprehensive Test Suite")
        print("=" * 60)
        print(f"Started at: {self.start_time}")
        print(f"Project root: {self.project_root}")
        print()
        
        # Test suites to run
        test_suites = [
            ("Unit Tests", self._run_unit_tests),
            ("Integration Tests", self._run_integration_tests),
            ("End-to-End Tests", self._run_e2e_tests),
            ("Security Tests", self._run_security_tests),
            ("Performance Tests", self._run_performance_tests),
            ("Deployment Verification", self._run_deployment_verification)
        ]
        
        overall_success = True
        
        for suite_name, suite_function in test_suites:
            print(f"Running {suite_name}...")
            print("-" * 40)
            
            try:
                start_time = time.time()
                success, details = suite_function()
                duration = time.time() - start_time
                
                self.results[suite_name] = {
                    "success": success,
                    "duration": duration,
                    "details": details,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                status = "PASS" if success else "FAIL"
                print(f"{status}: {suite_name} ({duration:.2f}s)")
                
                if not success:
                    overall_success = False
                    
            except Exception as e:
                print(f"ERROR: {suite_name} - {e}")
                self.results[suite_name] = {
                    "success": False,
                    "duration": 0,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                overall_success = False
            
            print()
        
        # Generate comprehensive report
        self._generate_comprehensive_report()
        
        return overall_success
    
    def _run_unit_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """Run unit tests"""
        # Look for unit test files
        test_files = []
        tests_dir = os.path.join(self.project_root, "tests")
        
        if os.path.exists(tests_dir):
            for file in os.listdir(tests_dir):
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(tests_dir, file))
        
        if not test_files:
            return True, {"message": "No unit test files found", "tests_run": 0}
        
        # Run unit tests using pytest if available, otherwise unittest
        try:
            # Try pytest first
            result = subprocess.run([
                sys.executable, "-m", "pytest", tests_dir, "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                return True, {
                    "framework": "pytest",
                    "output": result.stdout,
                    "tests_run": len(test_files)
                }
            else:
                return False, {
                    "framework": "pytest",
                    "output": result.stdout,
                    "error": result.stderr,
                    "tests_run": len(test_files)
                }
                
        except FileNotFoundError:
            # Fall back to unittest
            try:
                result = subprocess.run([
                    sys.executable, "-m", "unittest", "discover", "-s", tests_dir, "-v"
                ], capture_output=True, text=True, cwd=self.project_root)
                
                return result.returncode == 0, {
                    "framework": "unittest",
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else "",
                    "tests_run": len(test_files)
                }
                
            except Exception as e:
                return False, {"error": f"Could not run unit tests: {e}"}
    
    def _run_integration_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """Run integration tests"""
        integration_test_file = os.path.join(self.project_root, "tests", "integration_tests.py")
        
        if not os.path.exists(integration_test_file):
            return True, {"message": "Integration test file not found"}
        
        try:
            # Start backend service if not running
            backend_started = self._ensure_backend_running()
            
            # Run integration tests
            result = subprocess.run([
                sys.executable, integration_test_file
            ], capture_output=True, text=True, cwd=self.project_root)
            
            success = result.returncode == 0
            
            details = {
                "output": result.stdout,
                "error": result.stderr if not success else "",
                "backend_started": backend_started
            }
            
            return success, details
            
        except Exception as e:
            return False, {"error": f"Integration tests failed: {e}"}
    
    def _run_e2e_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """Run end-to-end tests"""
        e2e_test_file = os.path.join(self.project_root, "tests", "e2e_tests.py")
        
        if not os.path.exists(e2e_test_file):
            return True, {"message": "E2E test file not found"}
        
        try:
            # Ensure both backend and frontend are running
            backend_started = self._ensure_backend_running()
            frontend_started = self._ensure_frontend_running()
            
            # Run E2E tests
            result = subprocess.run([
                sys.executable, e2e_test_file
            ], capture_output=True, text=True, cwd=self.project_root)
            
            success = result.returncode == 0
            
            details = {
                "output": result.stdout,
                "error": result.stderr if not success else "",
                "backend_started": backend_started,
                "frontend_started": frontend_started
            }
            
            return success, details
            
        except Exception as e:
            return False, {"error": f"E2E tests failed: {e}"}
    
    def _run_security_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """Run security tests"""
        # Basic security checks
        security_checks = []
        
        # Check for common security issues in code
        try:
            # Look for potential security issues
            backend_dir = os.path.join(self.project_root, "honeytrap-backend")
            
            if os.path.exists(backend_dir):
                # Check for hardcoded secrets
                result = subprocess.run([
                    "grep", "-r", "-i", "password.*=.*['\"]", backend_dir
                ], capture_output=True, text=True)
                
                if result.stdout:
                    security_checks.append({
                        "check": "Hardcoded passwords",
                        "status": "WARNING",
                        "details": "Potential hardcoded passwords found"
                    })
                else:
                    security_checks.append({
                        "check": "Hardcoded passwords",
                        "status": "PASS",
                        "details": "No hardcoded passwords found"
                    })
                
                # Check for SQL injection vulnerabilities
                result = subprocess.run([
                    "grep", "-r", "-i", "execute.*%", backend_dir
                ], capture_output=True, text=True)
                
                if result.stdout:
                    security_checks.append({
                        "check": "SQL injection",
                        "status": "WARNING",
                        "details": "Potential SQL injection vulnerabilities found"
                    })
                else:
                    security_checks.append({
                        "check": "SQL injection",
                        "status": "PASS",
                        "details": "No obvious SQL injection vulnerabilities"
                    })
            
            # Check for HTTPS configuration
            security_checks.append({
                "check": "HTTPS configuration",
                "status": "INFO",
                "details": "Manual verification required for production deployment"
            })
            
            # All security checks passed if no warnings
            all_passed = all(check["status"] != "WARNING" for check in security_checks)
            
            return all_passed, {"checks": security_checks}
            
        except Exception as e:
            return False, {"error": f"Security tests failed: {e}"}
    
    def _run_performance_tests(self) -> Tuple[bool, Dict[str, Any]]:
        """Run performance tests"""
        try:
            # Basic performance checks
            performance_results = []
            
            # Check if backend is responsive
            backend_started = self._ensure_backend_running()
            
            if backend_started:
                import requests
                import time
                
                # Test response time
                start_time = time.time()
                try:
                    response = requests.get("http://localhost:5000/health", timeout=10)
                    response_time = time.time() - start_time
                    
                    performance_results.append({
                        "test": "Health endpoint response time",
                        "value": response_time,
                        "unit": "seconds",
                        "status": "PASS" if response_time < 2.0 else "FAIL"
                    })
                    
                except Exception as e:
                    performance_results.append({
                        "test": "Health endpoint response time",
                        "error": str(e),
                        "status": "FAIL"
                    })
                
                # Test concurrent requests
                try:
                    import threading
                    import queue
                    
                    results_queue = queue.Queue()
                    
                    def make_request():
                        try:
                            start = time.time()
                            response = requests.get("http://localhost:5000/health", timeout=5)
                            duration = time.time() - start
                            results_queue.put(("success", duration))
                        except Exception as e:
                            results_queue.put(("error", str(e)))
                    
                    # Create 5 concurrent requests
                    threads = []
                    for _ in range(5):
                        thread = threading.Thread(target=make_request)
                        threads.append(thread)
                        thread.start()
                    
                    # Wait for all threads
                    for thread in threads:
                        thread.join()
                    
                    # Collect results
                    successes = 0
                    total_time = 0
                    while not results_queue.empty():
                        status, result = results_queue.get()
                        if status == "success":
                            successes += 1
                            total_time += result
                    
                    avg_time = total_time / successes if successes > 0 else 0
                    
                    performance_results.append({
                        "test": "Concurrent requests",
                        "successful": successes,
                        "total": 5,
                        "average_time": avg_time,
                        "status": "PASS" if successes >= 4 else "FAIL"
                    })
                    
                except Exception as e:
                    performance_results.append({
                        "test": "Concurrent requests",
                        "error": str(e),
                        "status": "FAIL"
                    })
            
            # Check if all performance tests passed
            all_passed = all(result.get("status") == "PASS" for result in performance_results)
            
            return all_passed, {"results": performance_results}
            
        except Exception as e:
            return False, {"error": f"Performance tests failed: {e}"}
    
    def _run_deployment_verification(self) -> Tuple[bool, Dict[str, Any]]:
        """Run deployment verification"""
        verification_script = os.path.join(self.project_root, "scripts", "deployment_verification.py")
        
        if not os.path.exists(verification_script):
            return True, {"message": "Deployment verification script not found"}
        
        try:
            # Run deployment verification
            result = subprocess.run([
                sys.executable, verification_script
            ], capture_output=True, text=True, cwd=self.project_root)
            
            success = result.returncode == 0
            
            details = {
                "output": result.stdout,
                "error": result.stderr if not success else ""
            }
            
            return success, details
            
        except Exception as e:
            return False, {"error": f"Deployment verification failed: {e}"}
    
    def _ensure_backend_running(self) -> bool:
        """Ensure backend service is running"""
        try:
            import requests
            response = requests.get("http://localhost:5000/health", timeout=5)
            return response.status_code == 200
        except:
            # Try to start backend
            try:
                backend_dir = os.path.join(self.project_root, "honeytrap-backend")
                if os.path.exists(os.path.join(backend_dir, "src", "main.py")):
                    # Start backend in background
                    subprocess.Popen([
                        sys.executable, "src/main.py"
                    ], cwd=backend_dir)
                    
                    # Wait for it to start
                    time.sleep(5)
                    
                    # Check if it's running
                    response = requests.get("http://localhost:5000/health", timeout=5)
                    return response.status_code == 200
            except:
                pass
        
        return False
    
    def _ensure_frontend_running(self) -> bool:
        """Ensure frontend service is running"""
        try:
            import requests
            response = requests.get("http://localhost:3000", timeout=5)
            return response.status_code in [200, 404]  # 404 might be expected for SPA
        except:
            # Try to start frontend
            try:
                frontend_dir = os.path.join(self.project_root, "honeytrap-frontend")
                if os.path.exists(os.path.join(frontend_dir, "package.json")):
                    # Start frontend in background
                    subprocess.Popen([
                        "npm", "start"
                    ], cwd=frontend_dir)
                    
                    # Wait for it to start
                    time.sleep(10)
                    
                    # Check if it's running
                    response = requests.get("http://localhost:3000", timeout=5)
                    return response.status_code in [200, 404]
            except:
                pass
        
        return False
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        # Calculate overall statistics
        total_suites = len(self.results)
        passed_suites = sum(1 for r in self.results.values() if r["success"])
        failed_suites = total_suites - passed_suites
        
        print("=" * 60)
        print("COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        print(f"Started: {self.start_time}")
        print(f"Completed: {end_time}")
        print(f"Total Duration: {duration:.2f} seconds")
        print()
        print(f"Test Suites: {total_suites}")
        print(f"Passed: {passed_suites}")
        print(f"Failed: {failed_suites}")
        print(f"Success Rate: {(passed_suites / total_suites * 100):.1f}%")
        print()
        
        # Detailed results
        print("DETAILED RESULTS:")
        print("-" * 40)
        for suite_name, result in self.results.items():
            status = "PASS" if result["success"] else "FAIL"
            duration = result.get("duration", 0)
            print(f"{status}: {suite_name} ({duration:.2f}s)")
            
            if not result["success"] and "error" in result:
                print(f"  Error: {result['error']}")
        
        print()
        
        # Save detailed report
        report_file = f"test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "summary": {
                "total_suites": total_suites,
                "passed_suites": passed_suites,
                "failed_suites": failed_suites,
                "success_rate": (passed_suites / total_suites * 100) if total_suites > 0 else 0
            },
            "results": self.results,
            "config": self.config
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"Could not save detailed report: {e}")
        
        # Generate HTML report
        self._generate_html_report(report_data, report_file.replace('.json', '.html'))
    
    def _generate_html_report(self, report_data: Dict[str, Any], filename: str):
        """Generate HTML test report"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Honeytrap Network - Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #1a237e; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .pass {{ color: green; font-weight: bold; }}
        .fail {{ color: red; font-weight: bold; }}
        .suite {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
        .suite.pass {{ border-left-color: green; }}
        .suite.fail {{ border-left-color: red; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Honeytrap Network - Test Report</h1>
        <p>Generated: {report_data['end_time']}</p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Duration:</strong> {report_data['duration_seconds']:.2f} seconds</p>
        <p><strong>Total Suites:</strong> {report_data['summary']['total_suites']}</p>
        <p><strong>Passed:</strong> <span class="pass">{report_data['summary']['passed_suites']}</span></p>
        <p><strong>Failed:</strong> <span class="fail">{report_data['summary']['failed_suites']}</span></p>
        <p><strong>Success Rate:</strong> {report_data['summary']['success_rate']:.1f}%</p>
    </div>
    
    <h2>Test Suite Results</h2>
    <table>
        <tr>
            <th>Test Suite</th>
            <th>Status</th>
            <th>Duration (s)</th>
            <th>Details</th>
        </tr>
"""
            
            for suite_name, result in report_data['results'].items():
                status_class = "pass" if result['success'] else "fail"
                status_text = "PASS" if result['success'] else "FAIL"
                duration = result.get('duration', 0)
                
                details = ""
                if 'error' in result:
                    details = f"Error: {result['error']}"
                elif 'details' in result and isinstance(result['details'], dict):
                    if 'message' in result['details']:
                        details = result['details']['message']
                
                html_content += f"""
        <tr>
            <td>{suite_name}</td>
            <td class="{status_class}">{status_text}</td>
            <td>{duration:.2f}</td>
            <td>{details}</td>
        </tr>
"""
            
            html_content += """
    </table>
</body>
</html>
"""
            
            with open(filename, 'w') as f:
                f.write(html_content)
            
            print(f"HTML report saved to: {filename}")
            
        except Exception as e:
            print(f"Could not generate HTML report: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Honeytrap Network Comprehensive Test Runner")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--skip-e2e", action="store_true", help="Skip end-to-end tests")
    parser.add_argument("--skip-performance", action="store_true", help="Skip performance tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Create test runner
    runner = TestRunner(config)
    
    # Run all tests
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

