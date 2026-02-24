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

conn = get_db()
try:
    with conn.cursor() as cur:
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'client_payment';")
        columns = cur.fetchall()
        print("Columns in client_payment:")
        for col in columns:
            print(f"- {col['column_name']} ({col['data_type']})")
except Exception as e:
    print(f"Error: {e}")
finally:
    try:
        conn.close()
    except:
        pass
