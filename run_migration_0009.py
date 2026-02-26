
import sys
import os

# Add the current directory to sys.path so we can import app
sys.path.append(os.path.dirname(__file__))

try:
    from app.database import get_db
    from app.config import settings
    
    with get_db() as conn:
        with conn.cursor() as cur:
            # Read migration file
            migration_file = os.path.join(os.path.dirname(__file__), 'migrations', '0009_add_client_po_id_to_vendor_order.sql')
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            # Execute SQL
            cur.execute(sql)
            print("Migration 0009 applied successfully")
        conn.commit()
except Exception as e:
    print(f"Error applying migration: {e}")
    sys.exit(1)
