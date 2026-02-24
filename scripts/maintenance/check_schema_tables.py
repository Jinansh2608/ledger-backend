import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(host='localhost', port=5432, dbname='Nexgen_erp', user='postgres', password='toor', cursor_factory=RealDictCursor)
with conn.cursor() as cur:
    cur.execute('SET search_path TO "Finances";')
    
    # Get all tables with row counts
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'Finances' ORDER BY table_name;")
    print('\n📋 TABLES IN FINANCES SCHEMA:\n')
    tables = []
    for row in cur.fetchall():
        table_name = row['table_name']
        tables.append(table_name)
        # Get row count
        cur.execute(f"SELECT COUNT(*) as cnt FROM {table_name};")
        cnt = cur.fetchone()['cnt']
        print(f"  • {table_name:<30} {cnt:>6} rows")
    
    # Check for unused/redundant tables
    print('\n\n🔍 SCHEMA ANALYSIS:\n')
    
    # Check for tables that might be redundant
    redundant_candidates = {
        'billing_po': 'Check if used - links to vendor orders',
        'vendor_order': 'Check if used - for vendor purchases',
        'vendor_payment': 'Check if used - vendor payment tracking',
        'vendor_payment_link': 'Check if used - links vendor to payments',
        'proforma_invoice': 'Check if used - invoice management',
        'document': 'Check if used - document storage',
        'payment': 'Check if used - payment records'
    }
    
    print("Potentially unused tables (check usage):")
    for table, note in redundant_candidates.items():
        if table in tables:
            cur.execute(f"SELECT COUNT(*) as cnt FROM {table};")
            cnt = cur.fetchone()['cnt']
            status = "✅ OK" if cnt > 0 else "❌ EMPTY"
            print(f"  • {table:<25} {status:<10} ({note})")

conn.close()
