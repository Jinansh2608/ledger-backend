#!/usr/bin/env python3
"""
Comprehensive API-to-Schema Mismatch Report
Identifies all places where code queries/expects columns that don't exist in the actual schema
"""

from pathlib import Path
import re

print("=" * 120)
print("COMPREHENSIVE API-TO-SCHEMA MISMATCH AUDIT")
print("=" * 120)

# ============================================================================
# ACTUAL SCHEMA (from audit)
# ============================================================================
actual_schema = {
    'po_project_mapping': ['id', 'client_po_id', 'project_id', 'created_at'],
    'client_po_line_item': ['id', 'client_po_id', 'item_name', 'quantity', 'unit_price', 'total_price', 'hsn_code', 'unit', 'rate', 'gst_amount', 'gross_amount'],
    'billing_po_line_item': ['id', 'billing_po_id', 'item_description', 'quantity', 'unit_price', 'amount', 'created_at'],
    'vendor_order_line_item': ['id', 'vendor_order_id', 'item_description', 'quantity', 'unit_price', 'amount', 'created_at'],
    'client_po': ['id', 'client_id', 'project_id', 'po_number', 'po_date', 'po_value', 'receivable_amount', 'status', 'created_at', 'po_type', 'parent_po_id', 'agreement_date', 'notes', 'pi_number', 'pi_date', 'vendor_id', 'site_id', 'vendor_gstin', 'bill_to_gstin', 'vendor_address', 'bill_to_address', 'ship_to_address', 'subtotal', 'cgst', 'sgst', 'igst', 'total_tax', 'store_id'],
    'project': ['id', 'client_id', 'name', 'status', 'created_at', 'location', 'city', 'state', 'country', 'latitude', 'longitude'],
    'billing_po': ['id', 'client_id', 'po_number', 'amount', 'status', 'created_at'],
    'vendor_order': ['id', 'vendor_id', 'po_number', 'amount', 'status', 'created_at'],
    'vendor': ['id', 'name', 'address', 'gstin', 'created_at', 'contact_person', 'email', 'phone', 'payment_terms', 'status', 'updated_at'],
    'client': ['id', 'name', 'created_at'],
}

# ============================================================================
# EXPECTED SCHEMA (from code patterns)
# ============================================================================
expected_schema = {
    'po_project_mapping': ['id', 'client_po_id', 'project_id', 'created_at', 'is_primary', 'sequence_order'],  # CODE EXPECTS THESE
    'client_po_line_item': ['id', 'client_po_id', 'item_name', 'quantity', 'unit_price', 'total_price', 'created_at'],  # CODE EXPECTS created_at
}

# ============================================================================
# IDENTIFIED MISMATCHES
# ============================================================================
print("\n🔴 CRITICAL SCHEMA MISMATCHES\n")

# Mismatch 1: po_project_mapping
print("❌ TABLE: po_project_mapping")
print(f"  Actual columns: {', '.join(actual_schema['po_project_mapping'])}")
print(f"  Expected by code: {', '.join(expected_schema['po_project_mapping'])}")
print(f"  ⚠️ MISSING from actual schema: is_primary, sequence_order")
print(f"  Impact: Queries using these columns will FAIL")
print()

# Mismatch 2: client_po_line_item
print("❌ TABLE: client_po_line_item")
print(f"  Actual columns: {', '.join(actual_schema['client_po_line_item'])}")
print(f"  Expected by code (missing): created_at")
print(f"  ✅ EXTRA in actual schema: unit, hsn_code, rate, gst_amount, gross_amount")
print(f"  Impact: Queries selecting created_at will FAIL; New fields exist but code doesn't capture them")
print()

# ============================================================================
# FILES THAT NEED TO BE FIXED
# ============================================================================
print("\n📁 FILES REQUIRING FIXES\n")

fixes_needed = {
    'app/repository/po_management_repo.py': [
        'Remove is_primary from po_project_mapping queries',
        'Remove sequence_order from po_project_mapping queries',
        'Remove created_at from client_po_line_item select statements',
        'Add unit, hsn_code, rate, gst_amount, gross_amount to line item queries',
    ],
    'app/apis/po_management.py': [
        'Update response models to match actual columns',
        'Add new fields (unit, hsn_code, rate, gst_amount, gross_amount) to LineItemResponse',
        'Remove is_primary, sequence_order from PO response models',
    ],
}

for file, issues in fixes_needed.items():
    print(f"  • {file}")
    for issue in issues:
        print(f"    - {issue}")
print()

# ============================================================================
# DETAILED FIX REQUIREMENTS
# ============================================================================
print("\n" + "=" * 120)
print("DETAILED FIX REQUIREMENTS")
print("=" * 120 + "\n")

print("📋 FIX #1: po_project_mapping Queries")
print("-" * 120)
print("❌ CURRENT (WRONG):")
print("""
  SELECT ppm.id, ppm.is_primary, ppm.sequence_order
  FROM po_project_mapping ppm
  WHERE ppm.project_id = %s
""")
print("\n✅ CORRECT:")
print("""
  SELECT ppm.id, ppm.client_po_id, ppm.project_id
  FROM po_project_mapping ppm
  WHERE ppm.project_id = %s
""")
print()

print("📋 FIX #2: client_po_line_item Queries")
print("-" * 120)
print("❌ CURRENT (WRONG):")
print("""
  SELECT id, client_po_id, item_name, quantity, unit_price, total_price, created_at
  FROM client_po_line_item
  WHERE client_po_id = %s
""")
print("\n✅ CORRECT:")
print("""
  SELECT id, client_po_id, item_name, quantity, unit_price, total_price, 
         hsn_code, unit, rate, gst_amount, gross_amount
  FROM client_po_line_item
  WHERE client_po_id = %s
""")
print()

print("📋 FIX #3: Response Models")
print("-" * 120)
print("❌ CURRENT (WRONG):")
print("""
  class LineItemResponse(BaseModel):
      id: int
      item_name: str
      quantity: float
      unit_price: float
      total_price: float
      created_at: datetime  # THIS COLUMN DOESN'T EXIST
""")
print("\n✅ CORRECT:")
print("""
  class LineItemResponse(BaseModel):
      id: int
      item_name: str
      quantity: float
      unit_price: float
      total_price: float
      hsn_code: Optional[str]
      unit: Optional[str]
      rate: Optional[float]
      gst_amount: Optional[float]
      gross_amount: Optional[float]
""")
print()

print("\n" + "=" * 120)
print("NEXT STEPS")
print("=" * 120)
print("""
1. Review app/repository/po_management_repo.py for all column mismatches
2. Update po_project_mapping queries to remove is_primary, sequence_order
3. Update client_po_line_item queries to remove created_at, add new fields
4. Update all response models in app/apis/po_management.py
5. Update response models in other API files (billing_po.py, vendor_orders.py, etc.)
6. Run complete test suite to verify all endpoints work
7. Re-run test_project_line_items.py to confirm fixes
""")
print()

print("=" * 120)
print("AUDIT COMPLETE")
print("=" * 120)
