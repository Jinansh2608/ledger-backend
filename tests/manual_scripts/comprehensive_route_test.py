#!/usr/bin/env python3
"""
Comprehensive Route Testing for Nexgen Finance Backend
Tests all endpoints to identify bugs
"""

import requests
import json
import time
import sys
from datetime import date, timedelta
from urllib.parse import urljoin

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api"

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Test Results
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def print_header(title):
    print(f"\n{BLUE}{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}{RESET}\n")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    print(f"{YELLOW}ℹ {msg}{RESET}")

def test_endpoint(method, endpoint, name, data=None, params=None, files=None, expected_status=200):
    """Test an endpoint and return response"""
    url = urljoin(BASE_URL, endpoint)
    
    try:
        if method == "GET":
            resp = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            if files:
                resp = requests.post(url, data=data, files=files, params=params, timeout=10)
            else:
                resp = requests.post(url, json=data, params=params, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, json=data, params=params, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, params=params, timeout=10)
        else:
            print_error(f"{name}: Unknown method {method}")
            test_results['failed'] += 1
            return None
        
        # Check status
        if resp.status_code in [expected_status, 200, 201, 202, 204]:
            print_success(f"{name} ({method} {endpoint}) - Status: {resp.status_code}")
            test_results['passed'] += 1
            try:
                return resp.json() if resp.text else {}
            except:
                return {}
        else:
            error_msg = f"{name} ({method} {endpoint}) - Expected {expected_status}, got {resp.status_code}"
            print_error(error_msg)
            if resp.text:
                try:
                    print_info(f"  Response: {resp.json()}")
                except:
                    print_info(f"  Response: {resp.text[:200]}")
            test_results['failed'] += 1
            test_results['errors'].append(error_msg)
            return None
    except requests.exceptions.ConnectionError:
        error_msg = f"{name}: Cannot connect to {url}"
        print_error(error_msg)
        test_results['failed'] += 1
        test_results['errors'].append(error_msg)
        return None
    except Exception as e:
        error_msg = f"{name}: {str(e)}"
        print_error(error_msg)
        test_results['failed'] += 1
        test_results['errors'].append(error_msg)
        return None

# ============================================================================
# TESTS
# ============================================================================

def test_health():
    print_header("TESTING: Health & Status Endpoints")
    test_endpoint("GET", f"{API_PREFIX}/health", "Health Check")
    test_endpoint("GET", f"{API_PREFIX}/health/detailed", "Detailed Health Check")

def test_projects():
    print_header("TESTING: Projects Endpoints")
    
    # Create project
    project_data = {
        "name": "Test Project",
        "location": "Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India"
    }
    resp = test_endpoint("POST", f"{API_PREFIX}/projects", "Create Project", project_data)
    project_id = None
    if resp and "project" in resp:
        project_id = resp["project"].get("id") or resp["project"].get("project_id")
        print_info(f"  Project ID: {project_id}")
    
    # Get all projects
    test_endpoint("GET", f"{API_PREFIX}/projects", "Get All Projects", params={"skip": 0, "limit": 50})
    
    # Get project by ID
    if project_id:
        test_endpoint("GET", f"{API_PREFIX}/projects/{project_id}", f"Get Project {project_id}")
        
        # Update project
        update_data = {"name": "Updated Test Project", "city": "Bangalore"}
        test_endpoint("PUT", f"{API_PREFIX}/projects/{project_id}", f"Update Project {project_id}", update_data)
    
    return project_id

def test_vendors():
    print_header("TESTING: Vendors Endpoints")
    
    # Create vendor
    vendor_data = {
        "name": "Test Vendor",
        "contact_person": "John Doe",
        "email": "john@vendor.test",
        "phone": "9876543210",
        "address": "123 Test Street",
        "payment_terms": "30 days"
    }
    resp = test_endpoint("POST", f"{API_PREFIX}/vendors", "Create Vendor", vendor_data)
    vendor_id = None
    if resp and "vendor" in resp:
        vendor_id = resp["vendor"].get("id") or resp["vendor"].get("vendor_id")
        print_info(f"  Vendor ID: {vendor_id}")
    
    # Get all vendors
    test_endpoint("GET", f"{API_PREFIX}/vendors", "Get All Vendors")
    
    # Get vendors by status
    test_endpoint("GET", f"{API_PREFIX}/vendors", "Get Active Vendors", params={"status": "active"})
    
    # Get vendor by ID
    if vendor_id:
        test_endpoint("GET", f"{API_PREFIX}/vendors/{vendor_id}", f"Get Vendor {vendor_id}")
        
        # Update vendor
        update_data = {"email": "newemail@vendor.test", "payment_terms": "45 days"}
        test_endpoint("PUT", f"{API_PREFIX}/vendors/{vendor_id}", f"Update Vendor {vendor_id}", update_data)
        
        # Get vendor payments
        test_endpoint("GET", f"{API_PREFIX}/vendors/{vendor_id}/payments", f"Get Vendor {vendor_id} Payments")
        
        # Get vendor payment summary
        test_endpoint("GET", f"{API_PREFIX}/vendors/{vendor_id}/payment-summary", f"Get Vendor {vendor_id} Payment Summary")
    
    return vendor_id

def test_vendor_orders(project_id, vendor_id):
    print_header("TESTING: Vendor Orders Endpoints")
    
    if not project_id or not vendor_id:
        print_error("Skipping vendor orders - missing project or vendor")
        return None
    
    # Create vendor order
    order_data = {
        "vendor_id": vendor_id,
        "po_number": f"VO-TEST-{int(time.time())}",
        "po_date": str(date.today()),
        "po_value": 50000,
        "due_date": str(date.today() + timedelta(days=30)),
        "description": "Test vendor order"
    }
    resp = test_endpoint("POST", f"{API_PREFIX}/projects/{project_id}/vendor-orders", "Create Vendor Order", order_data)
    order_id = None
    if resp and "vendor_order" in resp:
        order_id = resp["vendor_order"].get("id") or resp["vendor_order"].get("vendor_order_id")
        print_info(f"  Vendor Order ID: {order_id}")
    
    # Get project vendor orders
    test_endpoint("GET", f"{API_PREFIX}/projects/{project_id}/vendor-orders", "Get Project Vendor Orders")
    
    # Get order details
    if order_id:
        test_endpoint("GET", f"{API_PREFIX}/vendor-orders/{order_id}", f"Get Vendor Order {order_id}")
        
        # Update vendor order
        update_data = {"po_value": 55000, "description": "Updated test order"}
        test_endpoint("PUT", f"{API_PREFIX}/projects/{project_id}/vendor-orders/{order_id}", f"Update Vendor Order {order_id}", update_data)
    
    return order_id

def test_vendor_payments(order_id):
    print_header("TESTING: Vendor Payments Endpoints")
    
    if not order_id:
        print_error("Skipping vendor payments - missing order")
        return None
    
    # Create payment
    payment_data = {
        "payment_date": str(date.today()),
        "amount": 25000,
        "payment_mode": "bank_transfer",
        "reference_number": f"VNDRPAY-{int(time.time())}",
        "notes": "Test vendor payment"
    }
    resp = test_endpoint("POST", f"{API_PREFIX}/vendor-orders/{order_id}/payments", "Create Vendor Payment", payment_data)
    payment_id = None
    if resp and "payment" in resp:
        payment_id = resp["payment"].get("id") or resp["payment"].get("payment_id")
        print_info(f"  Payment ID: {payment_id}")
    
    # Get vendor order payments
    test_endpoint("GET", f"{API_PREFIX}/vendor-orders/{order_id}/payments", "Get Vendor Order Payments")
    
    # Update payment
    if payment_id:
        update_data = {"amount": 26000, "status": "cleared"}
        test_endpoint("PUT", f"{API_PREFIX}/vendor-payments/{payment_id}", f"Update Vendor Payment {payment_id}", update_data)
    
    return payment_id

def test_file_uploads():
    print_header("TESTING: File Upload Endpoints")
    
    # Create session
    session_data = {
        "metadata": {"test": "session", "project": "test"},
        "ttl_hours": 24,
        "client_id": 1
    }
    resp = test_endpoint("POST", f"{API_PREFIX}/uploads/session", "Create Upload Session", session_data)
    session_id = None
    if resp and "session_id" in resp:
        session_id = resp["session_id"]
        print_info(f"  Session ID: {session_id}")
    
    # Get session
    if session_id:
        test_endpoint("GET", f"{API_PREFIX}/uploads/session/{session_id}", "Get Session Details")
        
        # List files
        test_endpoint("GET", f"{API_PREFIX}/uploads/session/{session_id}/files", "List Session Files")
        
        # Get stats
        test_endpoint("GET", f"{API_PREFIX}/uploads/session/{session_id}/stats", "Get Session Statistics")
    
    return session_id

def test_clients():
    print_header("TESTING: Clients Endpoints")
    test_endpoint("GET", f"{API_PREFIX}/clients", "Get Supported Clients")

def test_payments(project_id):
    print_header("TESTING: Payments Endpoints")
    
    if not project_id:
        print_error("Skipping payments - missing project")
        return
    
    # For now, just test that the endpoints exist
    # We'd need a real PO ID to test fully
    print_info("Payments endpoints require valid client_po_id from database")

def test_billing_po(project_id):
    print_header("TESTING: Billing PO Endpoints")
    
    if not project_id:
        print_error("Skipping billing PO - missing project")
        return
    
    # We'd need a real client_po_id to test fully
    print_info("Billing PO endpoints require valid client_po_id from database")

def test_documents(project_id):
    print_header("TESTING: Documents Endpoints")
    
    if not project_id:
        print_error("Skipping documents - missing project")
        return
    
    print_info("Document upload requires file - skipping in API test")

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    print(f"\n{BLUE}{'='*80}")
    print(f"  NEXGEN FINANCE BACKEND - COMPREHENSIVE ROUTE TEST")
    print(f"  Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Base URL: {BASE_URL}")
    print(f"{'='*80}{RESET}\n")
    
    # Wait for server
    print("Waiting for backend to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}{API_PREFIX}/health", timeout=2)
            print_success(f"Backend is ready (attempt {i+1}/{max_retries})")
            break
        except:
            if i == max_retries - 1:
                print_error("Backend failed to start - cannot proceed with tests")
                return
            print(f"  Attempt {i+1}/{max_retries}...")
            time.sleep(1)
    
    # Run tests in sequence
    test_health()
    test_clients()
    project_id = test_projects()
    vendor_id = test_vendors()
    order_id = test_vendor_orders(project_id, vendor_id)
    payment_id = test_vendor_payments(order_id)
    session_id = test_file_uploads()
    test_payments(project_id)
    test_billing_po(project_id)
    test_documents(project_id)
    
    # Print summary
    print_header("TEST SUMMARY")
    total = test_results['passed'] + test_results['failed']
    pass_rate = (test_results['passed'] / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {GREEN}{test_results['passed']}{RESET}")
    print(f"Failed: {RED}{test_results['failed']}{RESET}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results['errors']:
        print(f"\n{RED}Errors Found:{RESET}")
        for i, error in enumerate(test_results['errors'], 1):
            print(f"  {i}. {error}")
    
    print(f"\n{BLUE}{'='*80}{RESET}\n")

if __name__ == "__main__":
    main()
