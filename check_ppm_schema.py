from app.database import get_db

conn = get_db()
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'po_project_mapping'
            ORDER BY ordinal_position
        """)
        print('PO_PROJECT_MAPPING columns:')
        for row in cur.fetchall():
            print(f'  - {row["column_name"]}: {row["data_type"]}')
finally:
    conn.close()
