#!/usr/bin/env python3
"""Check database schema for upload tables"""
from app.database import get_db
from psycopg2.extras import RealDictCursor

conn = get_db()
try:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check upload_stats columns
        print("upload_stats columns:")
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'Finances' AND table_name = 'upload_stats'
            ORDER BY ordinal_position
        """)
        rows = cur.fetchall()
        for row in rows:
            print(f"  - {row['column_name']}: {row['data_type']}")
        
        print("\nupload_file columns:")
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'Finances' AND table_name = 'upload_file'
            ORDER BY ordinal_position
        """)
        rows = cur.fetchall()
        for row in rows:
            print(f"  - {row['column_name']}: {row['data_type']}")
        
        print("\nupload_session columns:")
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'Finances' AND table_name = 'upload_session'
            ORDER BY ordinal_position
        """)
        rows = cur.fetchall()
        for row in rows:
            print(f"  - {row['column_name']}: {row['data_type']}")
finally:
    conn.close()
