#!/usr/bin/env python3
"""Debug session repository with detailed output"""
from app.database import get_db
from datetime import datetime, timedelta
import uuid

# Create session  manually
session_id = f'debug_{uuid.uuid4().hex[:8]}'
expires_at = datetime.utcnow() + timedelta(hours=24)
metadata = {'test': 'true'}

print(f'Creating session: {session_id}')
print(f'Expires at: {expires_at}')

conn = get_db()
try:
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO upload_session (id, session_id, expires_at, metadata, status)
                VALUES (%s, %s, %s, %s, 'active')
                RETURNING id, session_id, created_at, expires_at, metadata, status
            """, (str(uuid.uuid4()), session_id, expires_at, "{}"))
            result = cur.fetchone()
            print(f'Created: {result}')

    # Now try to retrieve it with explicit connection freshness check
    with conn.cursor() as cur:
        # First verify it exists at all
        cur.execute("SELECT COUNT(*) as cnt FROM upload_session WHERE session_id = %s", (session_id,))
        count_result = cur.fetchone()
        print(f'\nDirect count query: {count_result}')
        
        # Check expiration with SQL
        cur.execute("""
            SELECT expires_at, expires_at < CURRENT_TIMESTAMP as is_expired,
                   CURRENT_TIMESTAMP as now_time
            FROM upload_session
            WHERE session_id = %s
        """, (session_id,))
        exp_result = cur.fetchone()
        print(f'Expiration check: {exp_result}')
        
        # Now full retrieval
        cur.execute("""
            SELECT id, session_id, created_at, expires_at, metadata, status
            FROM upload_session
            WHERE session_id = %s
        """, (session_id,))
        full_result = cur.fetchone()
        print(f'Full retrieval: {full_result}')
        
finally:
    conn.close()
