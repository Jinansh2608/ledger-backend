from app.database import get_db

conn = get_db()
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'client_po_line_item'
            ORDER BY ordinal_position
        """)
        print('CLIENT_PO_LINE_ITEM columns:')
        for row in cur.fetchall():
            print(f'  - {row["column_name"]}: {row["data_type"]}')
finally:
    conn.close()
