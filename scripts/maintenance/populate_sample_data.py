#!/usr/bin/env python3
"""
Populate sample data - Create test data in database for testing
"""
from app.database import get_db
from datetime import datetime, timedelta
import uuid

def create_test_projects():
    """Create sample projects"""
    print("Creating sample projects...")
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                projects = [
                    (1, "Nexgen Finance System", "active", "Mumbai", "Maharashtra", "India"),
                    (1, "Dashboard Project", "active", "Bangalore", "Karnataka", "India"),
                    (1, "API Automation", "active", "Delhi", "Delhi", "India"),
                ]
                
                for client_id, name, status, location, state, country in projects:
                    try:
                        cur.execute("""
                            INSERT INTO project (client_id, name, status, location, state, country, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        """, (client_id, name, status, location, state, country))
                    except:
                        # Skip if already exists
                        pass
                
                print(f"✓ Created {len(projects)} sample projects")
    finally:
        conn.close()

def create_test_vendors():
    """Create sample vendors"""
    print("Creating sample vendors...")
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                vendors = [
                    ("Vendor ABC", "test@vendorabc.com", "active"),
                    ("Supplier XYZ", "contact@supplierxyz.com", "active"),
                    ("Logistics Corp", "info@logisticscorp.com", "active"),
                ]
                
                for name, email, status in vendors:
                    try:
                        cur.execute("""
                            INSERT INTO vendor (name, email, status, created_at)
                            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                        """, (name, email, status))
                    except:
                        # Skip if already exists
                        pass
                
                print(f"✓ Created {len(vendors)} sample vendors")
    finally:
        conn.close()

def create_test_upload_sessions():
    """Create test upload sessions"""
    print("Creating test upload sessions...")
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                sessions = []
                for i in range(3):
                    session_id = f"test_session_{i+1}_{uuid.uuid4().hex[:8]}"
                    expires_at = datetime.utcnow() + timedelta(hours=24)
                    
                    try:
                        cur.execute("""
                            INSERT INTO upload_session (id, session_id, expires_at, metadata, status)
                            VALUES (%s, %s, %s, %s, 'active')
                        """, (str(uuid.uuid4()), session_id, expires_at, "{}"))
                        sessions.append(session_id)
                    except:
                        # Skip if already exists
                        pass
                
                print(f"✓ Created {len(sessions)} test upload sessions")
                return sessions
    finally:
        conn.close()

def main():
    """Populate all test data"""
    print("\n" + "="*60)
    print("  SAMPLE DATA POPULATION SCRIPT")
    print("="*60 + "\n")
    
    try:
        create_test_projects()
        create_test_vendors()
        create_test_upload_sessions()
        
        print("\n" + "="*60)
        print("✓ Sample data population complete!")
        print("="*60 + "\n")
        
        print("You can now:")
        print("  1. Run: python test_file_upload_system.py")
        print("  2. Run: python test_routes_validation.py")
        print("  3. Test endpoints via Postman or curl")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
