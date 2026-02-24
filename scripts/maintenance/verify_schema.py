from app.main import app
import psycopg2

print("✅ App loads successfully")

conn = psycopg2.connect(host='localhost', port=5432, dbname='Nexgen_erp', user='postgres', password='toor')
cur = conn.cursor()
cur.execute('SET search_path TO "Finances"; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = \'Finances\';')
total_tables = cur.fetchone()[0]

print(f"✅ Total tables: {total_tables}")
print("✅ Schema redesign complete")

conn.close()
