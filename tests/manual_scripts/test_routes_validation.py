#!/usr/bin/env python3
"""
Test all backend routes - quick test of all main API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001/api"

def test_endpoint(method, path, params=None, json_data=None, name=None):
    """Test a single endpoint"""
    if name is None:
        name = f"{method} {path}"
    
    try:
        url = f"{BASE_URL}{path}"
        if method.upper() == "GET":
            resp = requests.get(url, params=params, timeout=5)
        elif method.upper() == "POST":
            resp = requests.post(url, json=json_data, params=params, timeout=5)
        else:
            resp = requests.request(method, url, json=json_data, params=params, timeout=5)
        
        status_icon = "✓" if 200 <= resp.status_code < 300 else "✗"
        print(f"{status_icon} {name:50} [{resp.status_code}]")
        return resp.status_code < 400
    except Exception as e:
        print(f"✗ {name:50} [ERROR: {str(e)[:40]}]")
        return False

print("\n" + "="*80)
print("  BACKEND API ROUTES TEST SUMMARY")
print("="*80 + "\n")

# Health
print("HEALTH & BASIC:")
test_endpoint("GET", "/health", name="Health Check")

# Client Management
print("\nCLIENT MANAGEMENT:")
test_endpoint("GET", "/clients", name="Get Supported Clients")

# File Upload
print("\nFILE UPLOAD SESSIONS:")
test_endpoint("GET", "/uploads/session", name="List Sessions (if implemented)")
test_endpoint("POST", "/uploads/session", json_data={"client_id": 1, "ttl_hours": 24}, name="Create Session")

# PO Upload & Management
print("\nPO MANAGEMENT:")
test_endpoint("POST", "/po/upload", params={"client_id": 1}, name="Upload PO File (requires file)")
test_endpoint("GET", "/po", name="List POs (if implemented)")
test_endpoint("GET", "/client-po/1", name="Get Client PO by ID")

# Projects
print("\nPROJECT MANAGEMENT:")
test_endpoint("GET", "/projects", name="List Projects")
test_endpoint("GET", "/projects/1", name="Get Project by ID")
test_endpoint("POST", "/projects", json_data={"name": "Test", "description": "Test"}, name="Create Project")

# Documents
print("\nDOCUMENT MANAGEMENT:")
test_endpoint("GET", "/documents", name="List Documents")
test_endpoint("GET", "/documents/1", name="Get Document by ID")

# Payments
print("\nPAYMENT MANAGEMENT:")
test_endpoint("GET", "/payments", name="List Payments")
test_endpoint("GET", "/payments/1", name="Get Payment by ID")

# Vendors
print("\nVENDOR MANAGEMENT:")
test_endpoint("GET", "/vendors", name="List Vendors")
test_endpoint("GET", "/vendors/1", name="Get Vendor by ID")

# Vendor Orders
print("\nVENDOR ORDER MANAGEMENT:")
test_endpoint("GET", "/vendor-orders", name="List Vendor Orders")

# Vendor Payments
print("\nVENDOR PAYMENT MANAGEMENT:")
test_endpoint("GET", "/vendor-payments", name="List Vendor Payments")

print("\n" + "="*80)
print("  TEST COMPLETE")
print("="*80 + "\n")
