import pytest
import datetime
from fastapi.testclient import TestClient
from app.main import app

# Create a TestClient using the FastAPI app
client = TestClient(app)

# Helper function to generate a unique project name
def unique_project_name():
    return f"Test Project {datetime.datetime.now().isoformat()}"

# Helper function to generate a unique vendor name
def unique_vendor_name():
    return f"Test Vendor {datetime.datetime.now().isoformat()}"

# Helper to generate a unique PO number
def unique_po_number():
    return f"TEST-PO-{datetime.datetime.now().timestamp()}"

# Helper to generate a unique Vendor Order PO number
def unique_vo_po_number():
    return f"TEST-VO-{datetime.datetime.now().timestamp()}"

# --- Test Data Store (to share IDs between tests) ---
class TestData:
    project_id = None
    client_id = 99999 # Assuming a client with ID 99999 might not exist, but for creation we need a valid one. 
                      # In a real scenario, we should probably create a client first.
                      # Let's assume client_id 1 exists or we will try to create one if endpoints are available.
    client_po_id = None
    vendor_id = None
    vendor_order_id = None
    payment_id = None
    line_item_id = None

# We need a client ID. If there isn't an endpoint to create a client, we might need to assume one exists or mock it.
# However, for a "test everything" script, we should try to create dependencies.
# The `add_client_po` function takes a `client_id`.
# Let's assume client_id=1 exists for now, or the tests will fail if the DB is empty.
# If there is a route to create a client, we should use it. 
# Looking at the codebase, we don't see a `create_client` route in the provided file list (vendors is for vendors).
# Let's assume a client ID of 1 is available for testing or setup is done beforehand.
TEST_CLIENT_ID = 1 


# ==========================================
# 1. Health Check
# ==========================================
def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"

# ==========================================
# 2. Project Creation (Implicitly via PO or other means?)
#    - The docs show `POST /api/projects/{project_id}/po`
#    - It seems projects might be created automatically or we need an existing one.
#    - `po_management.py` has `create_po_for_project`.
#    - Let's try to create a PO which might create a project if it doesn't exist?
#    - Actually, `insert_client_po` in `client_po_repo.py` has `_get_or_create_project`.
#    - So we can start by creating a Manual PO to bootstrap a project.
# ==========================================

# ==========================================
# 3. Client PO Management
# ==========================================

def test_create_po_for_new_project():
    # We'll use a random large ID tosimulate a new project or current project
    # But wait, usually project creation is separate or implicit.
    # Let's try to create a new PO for a new project ID (e.g. 1001)
    # Note: If the DB has foreign key constraints on client_id, this might fail if client 1 doesn't exist.
    
    project_id = 1001 # Arbitrary ID for testing
    TestData.project_id = project_id
    
    payload = {
        "po_number": unique_po_number(),
        "po_date": datetime.date.today().isoformat(),
        "po_value": 50000.0,
        "po_type": "standard",
        "notes": "Automated Test PO"
    }
    
    # We need to pass client_id as a query param
    response = client.post(
        f"/api/projects/{project_id}/po?client_id={TEST_CLIENT_ID}", 
        json=payload
    )
    
    # If client 1 doesn't exist, this might fail with 500 or 400.
    # For a robust test script, we heavily rely on the DB state.
    if response.status_code == 500 and "violates foreign key constraint" in response.text:
        pytest.fail("Test failed: Client ID 1 does not exist in the database. Please ensure a client with ID 1 exists.")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    TestData.client_po_id = data["client_po_id"]
    print(f"\nCreated Client PO ID: {TestData.client_po_id} for Project: {project_id}")

def test_get_all_pos():
    response = client.get("/api/po")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["pos"]) > 0

def test_get_client_po_details():
    if not TestData.client_po_id:
        pytest.skip("No Client PO ID available")
        
    response = client.get(f"/api/client-po/{TestData.client_po_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["client_po_id"] == TestData.client_po_id

def test_update_client_po():
    if not TestData.client_po_id:
        pytest.skip("No Client PO ID available")

    payload = {
        "po_value": 55000.0, 
        "notes": "Updated via Test"
    }
    response = client.put(f"/api/po/{TestData.client_po_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["po"]["po_value"] == 55000.0

# ==========================================
# 4. Line Items (Client PO)
# ==========================================
def test_add_line_item_to_po():
    if not TestData.client_po_id:
        pytest.skip("No Client PO ID available")
        
    payload = {
        "item_name": "Test Item 1",
        "quantity": 10,
        "unit_price": 100.0
    }
    response = client.post(f"/api/po/{TestData.client_po_id}/line-items", json=payload)
    assert response.status_code == 200
    data = response.json()
    TestData.line_item_id = data["line_item"]["line_item_id"]
    assert data["line_item"]["total_price"] == 1000.0

def test_get_po_line_items():
    if not TestData.client_po_id:
        pytest.skip("No Client PO ID available")
        
    response = client.get(f"/api/po/{TestData.client_po_id}/line-items")
    assert response.status_code == 200
    assert len(response.json()["line_items"]) > 0

def test_update_line_item():
    if not TestData.line_item_id:
        pytest.skip("No Line Item ID available")
        
    payload = {
        "quantity": 20
    }
    response = client.put(f"/api/line-items/{TestData.line_item_id}", json=payload)
    assert response.status_code == 200
    # Price should update: 20 * 100 = 2000
    assert response.json()["line_item"]["total_price"] == 2000.0

def test_delete_line_item():
    if not TestData.line_item_id:
        pytest.skip("No Line Item ID available")
        
    response = client.delete(f"/api/line-items/{TestData.line_item_id}")
    assert response.status_code == 200
    TestData.line_item_id = None # Reset

# ==========================================
# 5. Vendor Management
# ==========================================
def test_create_vendor():
    payload = {
        "name": unique_vendor_name(),
        "contact_person": "Test Contact",
        "email": "test@vendor.com",
        "phone": "1234567890",
        "address": "123 Test St",
        "payment_terms": "Net 30"
    }
    response = client.post("/api/vendors", json=payload)
    assert response.status_code == 200
    data = response.json()
    TestData.vendor_id = data["vendor"]["id"]
    print(f"\nCreated Vendor ID: {TestData.vendor_id}")

def test_get_all_vendors():
    response = client.get("/api/vendors")
    assert response.status_code == 200
    assert len(response.json()["vendors"]) > 0

def test_get_vendor_details():
    if not TestData.vendor_id:
        pytest.skip("No Vendor ID available")
    
    response = client.get(f"/api/vendors/{TestData.vendor_id}")
    assert response.status_code == 200
    assert response.json()["vendor"]["id"] == TestData.vendor_id

def test_update_vendor():
    if not TestData.vendor_id:
        pytest.skip("No Vendor ID available")
        
    payload = {"contact_person": "Updated Contact"}
    response = client.put(f"/api/vendors/{TestData.vendor_id}", json=payload)
    assert response.status_code == 200
    assert response.json()["vendor"]["contact_person"] == "Updated Contact"

# ==========================================
# 6. Vendor Orders
# ==========================================
def test_create_vendor_order():
    if not TestData.project_id or not TestData.vendor_id:
        pytest.skip("Missing ProjectID or VendorID")

    payload = {
        "vendor_id": TestData.vendor_id,
        "po_number": unique_vo_po_number(),
        "po_date": datetime.date.today().isoformat(),
        "po_value": 10000.0,
        "due_date": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
        "description": "Test Vendor Order"
    }
    
    response = client.post(f"/api/projects/{TestData.project_id}/vendor-orders", json=payload)
    assert response.status_code == 200
    data = response.json()
    TestData.vendor_order_id = data["vendor_order"]["id"]
    print(f"\nCreated Vendor Order ID: {TestData.vendor_order_id}")

def test_get_project_vendor_orders():
    if not TestData.project_id:
        pytest.skip("No Project ID")
        
    response = client.get(f"/api/projects/{TestData.project_id}/vendor-orders")
    assert response.status_code == 200
    assert len(response.json()["vendor_orders"]) > 0

def test_get_vendor_order_details():
    if not TestData.vendor_order_id:
        pytest.skip("No Vendor Order ID")
        
    response = client.get(f"/api/vendor-orders/{TestData.vendor_order_id}")
    assert response.status_code == 200

def test_add_line_item_to_vendor_order():
    if not TestData.vendor_order_id:
        pytest.skip("No Vendor Order ID")
        
    payload = {
        "item_name": "VO Item 1",
        "quantity": 5,
        "unit_price": 200.0
    }
    response = client.post(f"/api/vendor-orders/{TestData.vendor_order_id}/line-items", json=payload)
    assert response.status_code == 200
    assert response.json()["line_item"]["total_price"] == 1000.0

# ==========================================
# 7. Payments (Client)
# ==========================================
def test_record_client_payment():
    if not TestData.client_po_id:
        pytest.skip("No Client PO ID")
        
    payload = {
        "payment_date": datetime.date.today().isoformat(),
        "amount": 5000.0,
        "payment_mode": "NEFT",
        "status": "cleared",
        "transaction_type": "credit",
        "reference_number": "TXN12345"
    }
    
    response = client.post(f"/api/po/{TestData.client_po_id}/payments", json=payload)
    assert response.status_code == 200
    data = response.json()
    TestData.payment_id = data["payment_id"]
    print(f"\nRecorded Payment ID: {TestData.payment_id}")

def test_get_po_payments():
    if not TestData.client_po_id:
        pytest.skip("No Client PO ID")
        
    response = client.get(f"/api/po/{TestData.client_po_id}/payments")
    assert response.status_code == 200
    assert len(response.json()["payments"]) > 0
    assert response.json()["summary"]["total_paid"] >= 5000.0

# ==========================================
# 8. Payments (Vendor)
# ==========================================
def test_record_vendor_payment():
    if not TestData.vendor_order_id:
        pytest.skip("No Vendor Order ID")
        
    payload = {
        "payment_date": datetime.date.today().isoformat(),
        "amount": 2000.0,
        "payment_mode": "IMPS",
        "reference_number": "V-TXN123"
    }
    
    response = client.post(f"/api/vendor-orders/{TestData.vendor_order_id}/payments", json=payload)
    assert response.status_code == 200

def test_get_vendor_order_payments():
    if not TestData.vendor_order_id:
        pytest.skip("No Vendor Order ID")

    response = client.get(f"/api/vendor-orders/{TestData.vendor_order_id}/payments")
    assert response.status_code == 200
    assert response.json()["payment_count"] > 0

# ==========================================
# 9. Vendor Payment Links
# ==========================================
def test_link_payment_to_vendor_order():
    if not TestData.vendor_order_id or not TestData.payment_id:
        pytest.skip("Missing VendorOrder or Payment ID")
        
    # Link the client payment (incoming) to the vendor order
    payload = {
        "payment_id": TestData.payment_id,
        "link_type": "incoming"
    }
    
    response = client.post(f"/api/vendor-orders/{TestData.vendor_order_id}/link-payment", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"

def test_get_linked_payments():
    if not TestData.vendor_order_id:
        pytest.skip("No Vendor Order ID")
        
    response = client.get(f"/api/vendor-orders/{TestData.vendor_order_id}/linked-payments")
    assert response.status_code == 200
    assert len(response.json()["incoming_payments"]) > 0

# ==========================================
# 10. Financial Summary & Enrichment
# ==========================================
def test_project_financial_summary():
    if not TestData.project_id:
        pytest.skip("No Project ID")
        
    response = client.get(f"/api/projects/{TestData.project_id}/financial-summary")
    assert response.status_code == 200
    data = response.json()
    assert "financial_summary" in data
    assert "net_profit" in data["financial_summary"]
    print("\nFinancial Summary Verified")

def test_enriched_pos():
    if not TestData.project_id:
        pytest.skip("No Project ID")
        
    response = client.get(f"/api/projects/{TestData.project_id}/po/enriched")
    assert response.status_code == 200
    data = response.json()
    assert len(data["pos"]) > 0
    # Check if payment details are enriched
    assert "payment_status" in data["pos"][0]

# ==========================================
# 11. Verbal Agreements
# ==========================================
def test_create_verbal_agreement():
    if not TestData.project_id:
        pytest.skip("No Project ID")
        
    payload = {
        "pi_number": "PI-TEST-001",
        "pi_date": datetime.date.today().isoformat(),
        "value": 25000.0,
        "notes": "Test Verbal Agreement"
    }
    
    # We assume client_id 1 exists from before
    response = client.post(
        f"/api/projects/{TestData.project_id}/verbal-agreement?client_id={TEST_CLIENT_ID}", 
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    global verbal_agreement_id 
    verbal_agreement_id = data["agreement_id"]

def test_get_verbal_agreements():
    if not TestData.project_id:
        pytest.skip("No Project ID")
        
    response = client.get(f"/api/projects/{TestData.project_id}/verbal-agreements")
    assert response.status_code == 200
    assert len(response.json()["agreements"]) > 0

# ==========================================
# 12. Cleanup (Optional - Delete created entities)
# ==========================================
# Note: In a real test environment, we might want to clean up.
# For now, we'll leave them to inspect the DB if needed or just rely on IDs.
# We will verify delete endpoints though.

def test_delete_vendor_payment():
    # Only if we created one... we need to fetch ID first from get_vendor_order_payments
    if not TestData.vendor_order_id:
        pytest.skip("No Vendor Order ID")
        
    # Get payments to find an ID
    res = client.get(f"/api/vendor-orders/{TestData.vendor_order_id}/payments")
    payments = res.json()["payments"]
    if payments:
        p_id = payments[0]["id"]
        del_res = client.delete(f"/api/vendor-payments/{p_id}")
        assert del_res.status_code == 200

def test_delete_client_payment():
    if not TestData.payment_id:
        pytest.skip("No Payment ID")
    
    # First we have to unlink if it's linked
    # But unlink API is: DELETE /api/vendor-orders/{vo_id}/payments/{p_id} (This unlinks)
    if TestData.vendor_order_id:
        client.delete(f"/api/vendor-orders/{TestData.vendor_order_id}/payments/{TestData.payment_id}")

    # Now delete the actual payment
    response = client.delete(f"/api/payments/{TestData.payment_id}")
    assert response.status_code == 200

def test_delete_vendor_order():
    if not TestData.vendor_order_id:
        pytest.skip("No Vendor Order ID")
        
    response = client.delete(f"/api/projects/{TestData.project_id}/vendor-orders/{TestData.vendor_order_id}")
    assert response.status_code == 200

def test_delete_vendor():
    if not TestData.vendor_id:
        pytest.skip("No Vendor ID")
        
    # Should succeed now that orders are deleted
    response = client.delete(f"/api/vendors/{TestData.vendor_id}")
    assert response.status_code == 200

# Run with: pytest test_backend_comprehensive.py
# If running directly:
if __name__ == "__main__":
    # Manually run functions if executed as script
    try:
        print("Running manual test sequence...")
        test_health_check()
        test_create_po_for_new_project()
        test_get_all_pos()
        test_get_client_po_details()
        test_update_client_po()
        test_add_line_item_to_po()
        test_get_po_line_items()
        test_update_line_item()
        test_delete_line_item()
        
        test_create_vendor()
        test_get_all_vendors()
        test_get_vendor_details()
        test_update_vendor()
        
        test_create_vendor_order()
        test_get_project_vendor_orders()
        test_get_vendor_order_details()
        test_add_line_item_to_vendor_order()
        
        test_record_client_payment()
        test_get_po_payments()
        
        test_record_vendor_payment()
        test_get_vendor_order_payments()
        
        test_link_payment_to_vendor_order()
        test_get_linked_payments()
        
        test_project_financial_summary()
        test_enriched_pos()
        
        test_create_verbal_agreement()
        test_get_verbal_agreements()
        
        # Cleanup
        test_delete_vendor_payment()
        test_delete_client_payment()
        test_delete_vendor_order()
        test_delete_vendor()
        
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
