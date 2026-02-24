"""
Comprehensive API Route Verification Tests
Verifies that all routes match frontend expectations
"""

import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def pass_test(self, name):
        self.passed += 1
        print(f"{GREEN}✓ PASS{RESET}: {name}")
    
    def fail_test(self, name, reason):
        self.failed += 1
        print(f"{RED}✗ FAIL{RESET}: {name}")
        print(f"  Reason: {reason}")
        self.errors.append(f"{name}: {reason}")
    
    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Summary: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"\n{RED}Failed Tests:{RESET}")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}\n")

results = TestResults()

# =====================================================
# 1. PURCHASE ORDERS (Client POs) TESTS
# =====================================================

print(f"\n{YELLOW}{'='*60}")
print("1. TESTING PURCHASE ORDERS ROUTES")
print(f"{'='*60}{RESET}\n")

# Test: GET /api/po - Get all POs
def test_get_all_pos():
    print("Testing: GET /api/po")
    try:
        response = requests.get(f"{BASE_URL}/po")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "data" in data, "Missing 'data' field in response"
        assert "pos" in data["data"], "Missing 'pos' field in data"
        assert "total_count" in data["data"], "Missing 'total_count' field"
        results.pass_test("GET /api/po - Get all POs")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/po - Get all POs", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/po - Get all POs", f"Exception: {str(e)}")
        return False

# Test: GET /api/po/{poId} - Get single PO
def test_get_single_po():
    print("Testing: GET /api/po/{poId}")
    try:
        # First get a PO ID from the all POs endpoint
        response = requests.get(f"{BASE_URL}/po")
        all_pos = response.json().get("data", {}).get("pos", [])
        
        if not all_pos:
            print(f"{YELLOW}  (Skipped: No POs available){RESET}")
            return True
        
        po_id = all_pos[0].get("id") or all_pos[0].get("client_po_id")
        response = requests.get(f"{BASE_URL}/po/{po_id}")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "data" in data, "Missing 'data' field"
        assert data["data"].get("id"), "Missing 'id' field"
        results.pass_test(f"GET /api/po/{po_id} - Get single PO")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/po/{poId} - Get single PO", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/po/{poId} - Get single PO", f"Exception: {str(e)}")
        return False

# Test: GET /api/po/{poId}/details - Get order details
def test_get_po_details():
    print("Testing: GET /api/po/{poId}/details")
    try:
        response = requests.get(f"{BASE_URL}/po")
        all_pos = response.json().get("data", {}).get("pos", [])
        
        if not all_pos:
            print(f"{YELLOW}  (Skipped: No POs available){RESET}")
            return True
        
        po_id = all_pos[0].get("id") or all_pos[0].get("client_po_id")
        response = requests.get(f"{BASE_URL}/po/{po_id}/details")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "data" in data, "Missing 'data' field"
        assert "payment_status" in data["data"], "Missing 'payment_status' field"
        results.pass_test(f"GET /api/po/{po_id}/details - Get order details")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/po/{poId}/details - Get order details", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/po/{poId}/details - Get order details", f"Exception: {str(e)}")
        return False

# =====================================================
# 2. PROJECTS TESTS
# =====================================================

print(f"\n{YELLOW}{'='*60}")
print("2. TESTING PROJECTS ROUTES")
print(f"{'='*60}{RESET}\n")

# Test: GET /api/projects - Get all projects
def test_get_projects():
    print("Testing: GET /api/projects")
    try:
        response = requests.get(f"{BASE_URL}/projects")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "projects" in data, "Missing 'projects' field"
        results.pass_test("GET /api/projects - Get all projects")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/projects - Get all projects", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/projects - Get all projects", f"Exception: {str(e)}")
        return False

# Test: GET /api/projects/{projectId}/po - Get project POs
def test_get_project_pos():
    print("Testing: GET /api/projects/{projectId}/po")
    try:
        response = requests.get(f"{BASE_URL}/projects")
        projects = response.json().get("projects", [])
        
        if not projects:
            print(f"{YELLOW}  (Skipped: No projects available){RESET}")
            return True
        
        project_id = projects[0]["id"]
        response = requests.get(f"{BASE_URL}/projects/{project_id}/po")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "pos" in data, "Missing 'pos' field"
        assert "project_id" in data, "Missing 'project_id' field"
        results.pass_test(f"GET /api/projects/{project_id}/po - Get project POs")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/projects/{projectId}/po - Get project POs", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/projects/{projectId}/po - Get project POs", f"Exception: {str(e)}")
        return False

# =====================================================
# 3. BILLING POs TESTS
# =====================================================

print(f"\n{YELLOW}{'='*60}")
print("3. TESTING BILLING POs ROUTES")
print(f"{'='*60}{RESET}\n")

# Test: GET /api/projects/{projectId}/pl-analysis - Get P&L analysis
def test_get_pl_analysis():
    print("Testing: GET /api/projects/{projectId}/pl-analysis")
    try:
        response = requests.get(f"{BASE_URL}/projects")
        projects = response.json().get("projects", [])
        
        if not projects:
            print(f"{YELLOW}  (Skipped: No projects available){RESET}")
            return True
        
        project_id = projects[0]["id"]
        response = requests.get(f"{BASE_URL}/projects/{project_id}/pl-analysis")
        if response.status_code == 404:
            print(f"{YELLOW}  (Skipped: No billing PO for project){RESET}")
            return True
        
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "data" in data, "Missing 'data' field"
        results.pass_test(f"GET /api/projects/{project_id}/pl-analysis - Get P&L analysis")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/projects/{projectId}/pl-analysis - Get P&L analysis", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/projects/{projectId}/pl-analysis - Get P&L analysis", f"Exception: {str(e)}")
        return False

# =====================================================
# 4. VENDORS TESTS
# =====================================================

print(f"\n{YELLOW}{'='*60}")
print("4. TESTING VENDORS ROUTES")
print(f"{'='*60}{RESET}\n")

# Test: GET /api/vendors - Get vendors
def test_get_vendors():
    print("Testing: GET /api/vendors")
    try:
        response = requests.get(f"{BASE_URL}/vendors")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "vendors" in data, "Missing 'vendors' field"
        results.pass_test("GET /api/vendors - Get vendors")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/vendors - Get vendors", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/vendors - Get vendors", f"Exception: {str(e)}")
        return False

# Test: GET /api/vendors with status filter
def test_get_vendors_filtered():
    print("Testing: GET /api/vendors?status=active")
    try:
        response = requests.get(f"{BASE_URL}/vendors?status=active")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        results.pass_test("GET /api/vendors?status=active - Vendors with status filter")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/vendors?status=active - Vendors with status filter", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/vendors?status=active - Vendors with status filter", f"Exception: {str(e)}")
        return False

# =====================================================
# 5. VENDOR ORDERS TESTS
# =====================================================

print(f"\n{YELLOW}{'='*60}")
print("5. TESTING VENDOR ORDERS ROUTES")
print(f"{'='*60}{RESET}\n")

# Test: GET /api/projects/{projectId}/vendor-orders
def test_get_vendor_orders():
    print("Testing: GET /api/projects/{projectId}/vendor-orders")
    try:
        response = requests.get(f"{BASE_URL}/projects")
        projects = response.json().get("projects", [])
        
        if not projects:
            print(f"{YELLOW}  (Skipped: No projects available){RESET}")
            return True
        
        project_id = projects[0]["id"]
        response = requests.get(f"{BASE_URL}/projects/{project_id}/vendor-orders")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "vendor_orders" in data, "Missing 'vendor_orders' field"
        results.pass_test(f"GET /api/projects/{project_id}/vendor-orders - Get vendor orders")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/projects/{projectId}/vendor-orders - Get vendor orders", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/projects/{projectId}/vendor-orders - Get vendor orders", f"Exception: {str(e)}")
        return False

# =====================================================================
# 6. PAYMENTS TESTS
# =====================================================================

print(f"\n{YELLOW}{'='*60}")
print("6. TESTING PAYMENTS ROUTES")
print(f"{'='*60}{RESET}\n")

# Test: GET /api/po/{poId}/payments
def test_get_po_payments():
    print("Testing: GET /api/po/{poId}/payments")
    try:
        response = requests.get(f"{BASE_URL}/po")
        all_pos = response.json().get("data", {}).get("pos", [])
        
        if not all_pos:
            print(f"{YELLOW}  (Skipped: No POs available){RESET}")
            return True
        
        po_id = all_pos[0].get("id") or all_pos[0].get("client_po_id")
        response = requests.get(f"{BASE_URL}/po/{po_id}/payments")
        assert response.status_code == 200, f"Status: {response.status_code}"
        data = response.json()
        assert data.get("status") == "SUCCESS", f"Status field: {data.get('status')}"
        assert "payments" in data, "Missing 'payments' field"
        results.pass_test(f"GET /api/po/{po_id}/payments - Get PO payments")
        return True
    except AssertionError as e:
        results.fail_test("GET /api/po/{poId}/payments - Get PO payments", str(e))
        return False
    except Exception as e:
        results.fail_test("GET /api/po/{poId}/payments - Get PO payments", f"Exception: {str(e)}")
        return False

# =====================================================================
# 7. FILE UPLOADS TESTS
# =====================================================================

print(f"\n{YELLOW}{'='*60}")
print("7. TESTING FILE UPLOADS ROUTES")
print(f"{'='*60}{RESET}\n")

# Test: GET /api/uploads/session/{sessionId}/files
def test_file_upload_routes():
    print("Testing: File upload routes (basic check)")
    try:
        # Just verify the endpoints exist
        response = requests.post(f"{BASE_URL}/uploads/session")
        if response.status_code in [200, 201]:
            results.pass_test("POST /api/uploads/session - Create session")
        else:
            results.fail_test("POST /api/uploads/session - Create session", f"Status: {response.status_code}")
        return True
    except Exception as e:
        results.fail_test("POST /api/uploads/session - Create session", f"Exception: {str(e)}")
        return False

# =====================================================================
# RUN ALL TESTS
# =====================================================================

print(f"\n{YELLOW}{'='*60}")
print("RUNNING ALL TESTS")
print(f"{'='*60}{RESET}\n")

# PO Tests
test_get_all_pos()
test_get_single_po()
test_get_po_details()

# Project Tests
test_get_projects()
test_get_project_pos()

# Billing PO Tests
test_get_pl_analysis()

# Vendor Tests
test_get_vendors()
test_get_vendors_filtered()

# Vendor Order Tests
test_get_vendor_orders()

# Payment Tests
test_get_po_payments()

# File Upload Tests
test_file_upload_routes()

# Print summary
results.print_summary()

# Exit with appropriate code
exit(0 if results.failed == 0 else 1)

