#!/usr/bin/env python3
"""Check where upload tables are created"""
from app.database import get_db

conn = get_db()
with conn.cursor() as cur:
    # Check both schemas
    cur.execute("""
        SELECT schemaname as table_schema, tablename 
        FROM pg_tables 
        WHERE tablename LIKE '%upload%' 
        ORDER BY schemaname, tablename
    """)
    results = cur.fetchall()
    if results:
        print('Upload tables found:')
        for row in results:
            print(f"  Schema: {row['table_schema']}, Table: {row['tablename']}")
    else:
        print('No upload tables found')

    # Check current search_path
    cur.execute("SHOW search_path")
    search_path = cur.fetchone()
    print(f"\nCurrent search_path: {search_path}")

conn.close()
