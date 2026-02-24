#!/usr/bin/env python3
"""Verify that sessions are being created in database"""
from app.database import get_db
import uuid
from datetime import datetime, timedelta

# Manually insert a session
conn = get_db()
try:
    with conn.cursor() as cur:
        session_id = f"test_sess_{uuid.uuid4().hex[:8]}"
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Insert
        cur.execute("""
            INSERT INTO upload_session (id, session_id, expires_at, metadata, status)
            VALUES (%s, %s, %s, %s, 'active')
        """, (str(uuid.uuid4()), session_id, expires_at, "{}"))
        
        print(f"✓ Inserted session: {session_id}")
        
        # Try to retrieve it
        cur.execute("SELECT session_id, status FROM upload_session WHERE session_id = %s", (session_id,))
        result = cur.fetchone()
        if result:
            print(f"✓ Retrieved session: {result}")
        else:
            print("✗ Session not found after insert!")
            
        # List all sessions
        cur.execute("SELECT COUNT(*) as count FROM upload_session")
        count_result = cur.fetchone()
        print(f"Total sessions in database: {count_result.get('count', 0)}")
    
    conn.commit()
except Exception as e:
    conn.rollback()
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
