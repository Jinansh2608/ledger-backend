#!/usr/bin/env python3
"""Test session creation via API and direct database verification"""
import requests
import json
from app.database import get_db
import time

BASE_URL = "http://127.0.0.1:8001/api"

print("="*60)
print("SESSION API TEST - DIRECT DATABASE VERIFICATION")
print("="*60)

# Step 1: Create session via API
print("\n1. Creating session via /api/uploads/session...")
payload = {
    "metadata": {"project": "test", "source": "direct_test"},
    "ttl_hours": 24,
    "client_id": 1
}

try:
    resp = requests.post(
        f"{BASE_URL}/uploads/session",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if resp.status_code == 200:
        session_id = data.get('session_id')
        print(f"\n✓ Session created: {session_id}")
        
        # Small delay to ensure the write completes
        time.sleep(0.5)
        
        # Step 2: Query database directly
        print(f"\n2. Querying database directly for session '{session_id}'...")
        from psycopg2.extras import RealDictCursor
        conn = get_db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM upload_session WHERE session_id = %s", (session_id,))
                result = cur.fetchone()
                if result:
                    print(f"✓ Found in database: {dict(result)}")
                else:
                    print(f"✗ NOT found in database (session_id={session_id})")
                    
                    # Check if any sessions exist
                    print(f"\n3. Checking if ANY sessions exist in database...")
                    cur.execute("SELECT COUNT(*) as count FROM upload_session")
                    count_result = cur.fetchone()
                    print(f"Total sessions in database: {count_result['count'] if count_result else 'unknown'}")
                    
                    if count_result and count_result['count'] > 0:
                        print(f"\n  Listing first 5 sessions:")
                        cur.execute("SELECT session_id, status, created_at FROM upload_session LIMIT 5")
                        rows = cur.fetchall()
                        for row in rows:
                            print(f"    - {dict(row)}")
        finally:
            conn.close()
        
        # Step 3: Try to get session via API
        print(f"\n4. Getting session via /api/uploads/session/{session_id}...")
        try:
            resp2 = requests.get(f"{BASE_URL}/uploads/session/{session_id}", timeout=10)
            print(f"Status: {resp2.status_code}")
            data2 = resp2.json()
            print(f"Response: {json.dumps(data2, indent=2, default=str)}")
            
            if resp2.status_code == 200:
                print(f"✓ Session retrieved via API")
            else:
                print(f"✗ Failed to retrieve session via API (status: {resp2.status_code})")
        except Exception as e:
            print(f"✗ Error: {e}")
    else:
        print(f"✗ Failed to create session (status: {resp.status_code})")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
