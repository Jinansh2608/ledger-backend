import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import app.database as db
    print("Module imported successfully")
    print("Module contents:", dir(db))
    print("Has get_db_connection?", hasattr(db, 'get_db_connection'))
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
