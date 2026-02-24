#!/usr/bin/env python3
"""
Backend API Test Suite - All Critical Routes
Tests file upload, parsing, and PO management workflows
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import sys
import os

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try to use colorama for Windows compatibility
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False

# Configuration
BASE_URL = "http://localhost:8000"
CLIENT_ID = 1
PROJECT_ID = 3
UPLOAD_BY = "test@nexgen.com"

# Test file path (create a dummy Excel file if needed)
TEST_FILE_PATH = r"C:\Users\Hitansh\Desktop\Nexgen\data\BAJAJ PO.xlsx"
MAX_RETRIES = 3
RETRY_DELAY = 1

# Color codes for output (with Windows fallback)
class Colors:
    if COLORAMA_AVAILABLE:
        HEADER = Fore.MAGENTA
        OKBLUE = Fore.CYAN
        OKCYAN = Fore.CYAN
        OKGREEN = Fore.GREEN
        WARNING = Fore.YELLOW
        FAIL = Fore.RED
        ENDC = Style.RESET_ALL
        BOLD = Style.BRIGHT
        UNDERLINE = ''
    else:
        # ANSI codes (may not work on Windows without colorama)
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'


class BackendTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = None
        self.file_id = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def print_header(self, text: str):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        sys.stdout.flush()

    def print_test(self, test_name: str):
        print(f"{Colors.BOLD}>> {test_name}{Colors.ENDC}")
        sys.stdout.flush()

    def print_success(self, message: str):
        print(f"{Colors.OKGREEN}[OK] {message}{Colors.ENDC}")
        self.tests_passed += 1
        sys.stdout.flush()

    def print_error(self, message: str):
        print(f"{Colors.FAIL}[FAIL] {message}{Colors.ENDC}")
        self.tests_failed += 1
        sys.stdout.flush()

    def print_info(self, message: str):
        print(f"{Colors.OKCYAN}[INFO] {message}{Colors.ENDC}")
        sys.stdout.flush()

    def print_warning(self, message: str):
        print(f"{Colors.WARNING}[WARN] {message}{Colors.ENDC}")
        sys.stdout.flush()
    
    def make_request(self, method, url, max_retries=MAX_RETRIES, **kwargs):
        """Make HTTP request with retry logic"""
        last_error = None
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    return requests.get(url, **kwargs)
                elif method.upper() == 'POST':
                    return requests.post(url, **kwargs)
                elif method.upper() == 'PUT':
                    return requests.put(url, **kwargs)
                elif method.upper() == 'DELETE':
                    return requests.delete(url, **kwargs)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                raise
        if last_error:
            raise last_error

    # ==================== SESSION MANAGEMENT ====================

    def test_create_session(self) -> bool:
        """Test: Create Upload Session"""
        self.print_test("TEST 1: Create Upload Session")

        try:
            payload = {
                "client_id": CLIENT_ID,
                "metadata": {
                    "project_id": PROJECT_ID,
                    "upload_type": "po",
                    "description": "Test PO upload"
                },
                "ttl_hours": 24
            }

            response = requests.post(
                f"{self.base_url}/api/uploads/session",
                json=payload,
                timeout=10
            )

            # Accept both 200 and 201 responses
            if response.status_code in [200, 201]:
                try:
                    data = response.json()
                    self.session_id = data.get("id") or data.get("session_id")
                    if not self.session_id:
                        self.print_error(f"Response missing 'id' or 'session_id' field")
                        self.print_info(f"Response: {json.dumps(data, indent=2)}")
                        return False
                    self.print_success(f"Session created: {self.session_id}")
                    resp_str = json.dumps(data, indent=2)
                    self.print_info(f"Response: {resp_str[:300]}..." if len(resp_str) > 300 else f"Response: {resp_str}")
                    return True
                except json.JSONDecodeError as e:
                    self.print_error(f"Failed to parse JSON response: {str(e)}")
                    return False
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.print_info(f"Response: {response.text[:300]}")
                return False

        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to server. Is it running?")
            return False
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    def test_get_session(self) -> bool:
        """Test: Get Session Details"""
        self.print_test("TEST 2: Get Session Details")

        if not self.session_id:
            self.print_error("No session_id available. Run test_create_session first.")
            return False

        try:
            response = requests.get(
                f"{self.base_url}/api/uploads/session/{self.session_id}",
                timeout=10
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.print_success(f"Session retrieved successfully")
                    resp_str = json.dumps(data, indent=2)
                    self.print_info(f"Response: {resp_str[:300]}..." if len(resp_str) > 300 else f"Response: {resp_str}")
                    return True
                except json.JSONDecodeError as e:
                    self.print_error(f"Failed to parse JSON response: {str(e)}")
                    return False
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.print_info(f"Response: {response.text[:300]}")
                return False

        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    # ==================== FILE UPLOAD ====================

    def test_upload_file_to_session(self) -> bool:
        """Test: Upload File to Session (Auto-Parse)"""
        self.print_test("TEST 3: Upload File to Session")

        if not self.session_id:
            self.print_error("No session_id available. Run test_create_session first.")
            return False

        # Check if test file exists
        if not Path(TEST_FILE_PATH).exists():
            self.print_warning(f"Test file '{TEST_FILE_PATH}' not found. Skipping file upload test.")
            self.print_warning("To test file upload, provide a valid Excel file.")
            return False

        try:
            with open(TEST_FILE_PATH, 'rb') as f:
                files = {
                    'file': (TEST_FILE_PATH, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                data = {
                    'uploaded_by': UPLOAD_BY,
                    'po_number': 'PO-TEST-001',
                    'auto_parse': 'true'
                }

                response = requests.post(
                    f"{self.base_url}/api/uploads/session/{self.session_id}/files",
                    files=files,
                    data=data,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    resp_data = response.json()
                    self.file_id = resp_data.get("id") or resp_data.get("file_id")
                    self.print_success(f"File uploaded: {self.file_id}")
                    self.print_info(f"Response: {json.dumps(resp_data, indent=2)}")
                    return True
                else:
                    self.print_error(f"Failed with status {response.status_code}")
                    self.print_info(f"Response: {response.text}")
                    return False

        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    def test_direct_po_upload(self) -> bool:
        """Test: Direct PO Upload & Parse"""
        self.print_test("TEST 4: Direct PO Upload & Parse (Recommended)")

        if not Path(TEST_FILE_PATH).exists():
            self.print_warning(f"Test file '{TEST_FILE_PATH}' not found. Skipping test.")
            return False

        try:
            with open(TEST_FILE_PATH, 'rb') as f:
                files = {
                    'file': (Path(TEST_FILE_PATH).name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                }
                data = {
                    'uploaded_by': UPLOAD_BY,
                    'auto_save': 'true'
                }
                params = {
                    'client_id': CLIENT_ID,
                    'project_id': PROJECT_ID
                }

                response = requests.post(
                    f"{self.base_url}/api/uploads/po/upload",
                    files=files,
                    data=data,
                    params=params,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    try:
                        resp_data = response.json()
                        self.print_success(f"PO uploaded and parsed successfully")
                        resp_str = json.dumps(resp_data, indent=2)
                        self.print_info(f"Response: {resp_str[:500]}..." if len(resp_str) > 500 else f"Response: {resp_str}")
                        return True
                    except json.JSONDecodeError:
                        self.print_success(f"PO uploaded and parsed (no JSON response)")
                        return True
                else:
                    self.print_error(f"Failed with status {response.status_code}")
                    self.print_info(f"Response: {response.text[:300]}")
                    return False

        except IOError as e:
            self.print_error(f"File I/O error: {str(e)}")
            return False
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    # ==================== FILE MANAGEMENT ====================

    def test_list_session_files(self) -> bool:
        """Test: List Session Files"""
        self.print_test("TEST 5: List Session Files")

        if not self.session_id:
            self.print_error("No session_id available. Run test_create_session first.")
            return False

        try:
            params = {
                'skip': 0,
                'limit': 50
            }

            response = requests.get(
                f"{self.base_url}/api/uploads/session/{self.session_id}/files",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                
                # Handle different response formats
                file_count = 0
                if isinstance(data, dict) and "files" in data:
                    file_count = len(data.get("files", []))
                elif isinstance(data, list):
                    file_count = len(data)
                elif isinstance(data, dict):
                    # Try to get count from response metadata
                    file_count = data.get("count", 0)
                    
                self.print_success(f"Listed session files ({file_count} files)")
                resp_str = json.dumps(data, indent=2)
                self.print_info(f"Response: {resp_str[:500]}..." if len(resp_str) > 500 else f"Response: {resp_str}")
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.print_info(f"Response: {response.text}")
                return False

        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    def test_download_file(self) -> bool:
        """Test: Download File"""
        self.print_test("TEST 6: Download File")

        if not self.session_id or not self.file_id:
            self.print_warning("No file_id available. Skipping download test.")
            self.print_info("Note: Complete test_upload_file_to_session first to get file_id")
            return False

        try:
            response = requests.get(
                f"{self.base_url}/api/uploads/session/{self.session_id}/files/{self.file_id}/download",
                timeout=30
            )

            if response.status_code == 200:
                file_size = len(response.content)
                self.print_success(f"File downloaded ({file_size} bytes)")
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                return False

        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    def test_delete_file(self) -> bool:
        """Test: Delete File"""
        self.print_test("TEST 7: Delete File")

        if not self.session_id or not self.file_id:
            self.print_warning("No file_id available. Skipping delete test.")
            return False

        try:
            response = requests.delete(
                f"{self.base_url}/api/uploads/session/{self.session_id}/files/{self.file_id}",
                timeout=10
            )

            if response.status_code in [200, 204]:
                self.print_success(f"File deleted successfully")
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.print_info(f"Response: {response.text}")
                return False

        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    # ==================== BULK OPERATIONS ====================

    def test_bulk_upload(self) -> bool:
        """Test: Bulk Upload Bajaj POs"""
        self.print_test("TEST 8: Bulk Upload Bajaj POs")

        if not Path(TEST_FILE_PATH).exists():
            self.print_warning(f"Test file '{TEST_FILE_PATH}' not found. Skipping bulk test.")
            return False

        try:
            with open(TEST_FILE_PATH, 'rb') as f:
                files = [
                    ('files', (Path(TEST_FILE_PATH).name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))
                ]
                params = {
                    'client_id': CLIENT_ID,
                    'project_id': PROJECT_ID
                }

                response = requests.post(
                    f"{self.base_url}/api/bajaj-po/bulk",
                    files=files,
                    params=params,
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    resp_data = response.json()
                    self.print_success(f"Bulk upload successful")
                    response_str = json.dumps(resp_data, indent=2)
                    self.print_info(f"Response: {response_str[:500]}..." if len(response_str) > 500 else f"Response: {response_str}")
                    return True
                else:
                    self.print_error(f"Failed with status {response.status_code}")
                    self.print_info(f"Response: {response.text[:500]}")
                    return False

        except IOError as e:
            self.print_error(f"File I/O error: {str(e)}")
            return False
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    # ==================== CLEANUP ====================

    def test_delete_session(self) -> bool:
        """Test: Delete Session"""
        self.print_test("TEST 9: Delete Session")

        if not self.session_id:
            self.print_error("No session_id available.")
            return False

        try:
            response = requests.delete(
                f"{self.base_url}/api/uploads/session/{self.session_id}",
                timeout=10
            )

            if response.status_code in [200, 204]:
                self.print_success(f"Session deleted successfully")
                return True
            else:
                self.print_error(f"Failed with status {response.status_code}")
                self.print_info(f"Response: {response.text}")
                return False

        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    # ==================== UTILITIES ====================

    def test_health_check(self) -> bool:
        """Test: Health Check"""
        self.print_test("TEST 0: Health Check (Connectivity)")

        try:
            response = self.make_request(
                'GET',
                f"{self.base_url}/api/health",
                timeout=5,
                max_retries=2
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    self.print_success(f"Server is running and healthy")
                    resp_str = json.dumps(data, indent=2)
                    self.print_info(f"Response: {resp_str[:200]}..." if len(resp_str) > 200 else f"Response: {resp_str}")
                except json.JSONDecodeError:
                    self.print_success(f"Server is running and healthy (no JSON response)")
                return True
            else:
                self.print_warning(f"Server returned status {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to server at " + self.base_url)
            self.print_info("Make sure the backend is running: python run.py")
            return False
        except requests.exceptions.Timeout:
            self.print_error("Connection timeout - server is taking too long to respond")
            return False
        except Exception as e:
            self.print_error(f"Exception: {str(e)}")
            return False

    # ==================== RUN ALL TESTS ====================

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.print_header("BACKEND API TEST SUITE - CRITICAL ROUTES")

        print(f"Base URL: {Colors.BOLD}{self.base_url}{Colors.ENDC}")
        print(f"Client ID: {Colors.BOLD}{CLIENT_ID}{Colors.ENDC}")
        print(f"Project ID: {Colors.BOLD}{PROJECT_ID}{Colors.ENDC}")
        print(f"Test File: {Colors.BOLD}{TEST_FILE_PATH}{Colors.ENDC}\n")

        # Health check first
        if not self.test_health_check():
            self.print_header("TESTS ABORTED - SERVER NOT RUNNING")
            return

        print()
        time.sleep(1)

        # Session management
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}SESSION MANAGEMENT{Colors.ENDC}")
        print("-" * 70)
        self.test_create_session()
        time.sleep(0.5)
        self.test_get_session()
        time.sleep(0.5)

        # File operations
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}FILE UPLOAD & PARSING{Colors.ENDC}")
        print("-" * 70)
        self.test_upload_file_to_session()
        time.sleep(0.5)
        self.test_direct_po_upload()
        time.sleep(0.5)

        # File management
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}FILE MANAGEMENT{Colors.ENDC}")
        print("-" * 70)
        self.test_list_session_files()
        time.sleep(0.5)
        self.test_download_file()
        time.sleep(0.5)

        # Bulk operations
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}BULK OPERATIONS{Colors.ENDC}")
        print("-" * 70)
        self.test_bulk_upload()
        time.sleep(0.5)

        # Cleanup
        print(f"\n{Colors.BOLD}{Colors.OKBLUE}CLEANUP{Colors.ENDC}")
        print("-" * 70)
        # Create a new session for cleanup test
        temp_tester = BackendTester(self.base_url)
        temp_tester.test_create_session()
        if temp_tester.session_id:
            temp_tester.test_delete_session()

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0

        self.print_header("TEST RESULTS SUMMARY")

        print(f"{Colors.BOLD}Total Tests:{Colors.ENDC} {total}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}Passed:{Colors.ENDC} {self.tests_passed}")
        print(f"{Colors.FAIL}{Colors.BOLD}Failed:{Colors.ENDC} {self.tests_failed}")
        print(f"{Colors.BOLD}Pass Rate:{Colors.ENDC} {pass_rate:.1f}%\n")

        if self.tests_failed == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}SUCCESS - ALL TESTS PASSED!{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}{Colors.BOLD}WARNING - SOME TESTS FAILED - Review output above{Colors.ENDC}")

        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def main():
    """Main entry point"""
    tester = BackendTester(BASE_URL)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
