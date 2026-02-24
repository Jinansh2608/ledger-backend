import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(host='localhost', port=5432, dbname='Nexgen_erp', user='postgres', password='toor', cursor_factory=RealDictCursor)
with conn.cursor() as cur:
    cur.execute('SET search_path TO "Finances";')
    
    tables = ['client', 'vendor', 'project', 'site', 'client_po', 'upload_session', 'upload_file']
    
    for table in tables:
        print(f"\n{table.upper()} columns:")
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position;")
        for row in cur.fetchall():
            print(f"  {row['column_name']}: {row['data_type']}")

conn.close()
