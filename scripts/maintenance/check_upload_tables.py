#!/usr/bin/env python3
"""Check if upload tables exist in database"""
from app.database import get_db

try:
    conn = get_db()
    with conn.cursor() as cur:
        # List all tables
        cur.execute("""SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename""")
        tables = [list(t.values())[0] for t in cur.fetchall()]
        print("Tables in database:")
        for t in sorted(tables):
            print(f"  - {t}")
        
        print("\nLooking for upload tables...")
        upload_tables = [t for t in tables if 'upload' in t.lower()]
        if upload_tables:
            print("Found upload tables:")
            for t in upload_tables:
                print(f"  - {t}")
        else:
            print("No upload tables found!")
            
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
