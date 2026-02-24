#!/usr/bin/env python3
"""Test is_expired logic directly"""
from app.database import get_db

session_id = 'test_sess_0a9cecdf'

conn = get_db()
try:
    with conn.cursor() as cur:
        # Test the exact SQL from is_session_expired
        cur.execute("""
            SELECT expires_at < CURRENT_TIMESTAMP as is_expired
            FROM upload_session
            WHERE session_id = %s
        """, (session_id,))
        
        result = cur.fetchone()
        print(f'Result from is_expired query: {result}')
        print(f'Type: {type(result)}')
        if result:
            print(f'is_expired value: {result["is_expired"]}')
        else:
            print('Result is None!')
finally:
    conn.close()
