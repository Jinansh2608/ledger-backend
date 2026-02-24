#!/usr/bin/env python3
"""Check project table schema"""
from app.database import get_db
from psycopg2.extras import RealDictCursor

conn = get_db()
try:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'Finances' AND table_name = 'project'
            ORDER BY ordinal_position
        """)
        rows = cur.fetchall()
        print("project table columns:")
        for row in rows:
            print(f"  - {row['column_name']}: {row['data_type']}")
finally:
    conn.close()
