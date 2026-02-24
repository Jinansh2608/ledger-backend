#!/usr/bin/env python3
"""Debug session creation and retrieval"""
from app.modules.file_uploads.services.session_service import SessionService
from app.modules.file_uploads.repositories.file_repository import UploadSessionRepository
from app.database import get_db
import time

print("="*60)
print("SESSION SERVICE DEBUG")
print("="*60)

# Step 1: Create a session
print("\n1. Creating session...")
session = SessionService.create_session(
    metadata={'test': 'debug'},
    ttl_hours=24
)
print(f"Created: {session}")
session_id = session['session_id']
print(f"Session ID: {session_id}")

# Step 2: Check if it exists in database directly
print(f"\n2. Querying database directly for session '{session_id}'...")
conn = get_db()
try:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM upload_session WHERE session_id = %s", (session_id,))
        result = cur.fetchone()
        print(f"Direct query result: {result}")
finally:
    conn.close()

# Step 3: Check expiration status  
print(f"\n3. Checking if session is expired...")
is_expired = UploadSessionRepository.is_session_expired(session_id)
print(f"is_session_expired(): {is_expired}")

# Step 4: Try to get it through repository
print(f"\n4. Retrieving through repository...")
retrieved = UploadSessionRepository.get_session(session_id)
print(f"get_session(): {retrieved}")

# Step 5: Try with file count
print(f"\n5. Retrieving with file count...")
retrieved_with_count = UploadSessionRepository.get_session_with_file_count(session_id)
print(f"get_session_with_file_count(): {retrieved_with_count}")

# Step 6: Try through service
print(f"\n6. Retrieving through service...")
service_result = SessionService.get_session(session_id)
print(f"SessionService.get_session(): {service_result}")

print("\n" + "="*60)
