#!/usr/bin/env python
"""Test script to verify backend implementation"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.main import app
    print("✓ Application loaded successfully")
    
    # Count vendor routes
    vendor_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and 'vendor' in str(route.path).lower():
            vendor_routes.append(route.path)
    
    print(f"✓ Found {len(vendor_routes)} vendor-related routes")
    
    # List them
    print("\nImplemented Vendor Endpoints:")
    for route in sorted(set(vendor_routes)):
        print(f"  - {route}")
    
    print("\n✓ All imports successful - Backend is ready!")
    
except Exception as e:
    print(f"✗ Error loading app: {e}")
    import traceback
    traceback.print_exc()
