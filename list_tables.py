from app.database import get_db

conn = get_db()
try:
    with conn.cursor() as cur:
        # Try to get all tables without schema filter
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY tablename
        """)
        tables = [row['tablename'] for row in cur.fetchall()]
        print(f"Found {len(tables)} tables:")
        for t in tables:
            print(f"  - {t}")
finally:
    conn.close()
