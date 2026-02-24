import sys
import os
from pathlib import Path

# Add Backend to python path
backend_path = Path(__file__).parent.parent.parent.absolute()
sys.path.append(str(backend_path))

try:
    from dotenv import load_dotenv
    load_dotenv(backend_path / '.env')
except ImportError:
    pass

from app.database import get_db

migration_file = backend_path / 'migrations' / '0007_add_payment_mode.sql'

if not migration_file.exists():
    print(f"Error: Migration file not found at {migration_file}", file=sys.stderr)
    sys.exit(1)

print(f"Applying migration: {migration_file}")
with open(migration_file, 'r') as f:
    sql = f.read()

try:
    conn = get_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    print("Migration applied successfully")
except Exception as e:
    print(f"Migration failed: {e}", file=sys.stderr)
    sys.exit(1)
finally:
    try:
        conn.close()
    except:
        pass
