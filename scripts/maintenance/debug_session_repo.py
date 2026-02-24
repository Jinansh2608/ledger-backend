#!/usr/bin/env python3
"""Debug session repository"""
from app.modules.file_uploads.repositories.file_repository import UploadSessionRepository
from datetime import datetime, timedelta
import uuid

# Create session
session_id = f'debug_{uuid.uuid4().hex[:8]}'
expires_at = datetime.utcnow() + timedelta(hours=24)
metadata = {'test': 'true'}

print(f'Creating session: {session_id}')
result = UploadSessionRepository.create_session(
    session_id=session_id,
    expires_at=expires_at,
    metadata=metadata
)
print(f'Created: {result}')

# Try to retrieve
print(f'\nRetrieving session...')
retrieved = UploadSessionRepository.get_session(session_id)
print(f'Retrieved: {retrieved}')

# Try with file count
print(f'\nRetrieving with file count...')
retrieved_with_count = UploadSessionRepository.get_session_with_file_count(session_id)
print(f'Retrieved with count: {retrieved_with_count}')

# Check expiration  
print(f'\nChecking expiration...')
is_expired = UploadSessionRepository.is_session_expired(session_id)
print(f'Is expired: {is_expired}')
