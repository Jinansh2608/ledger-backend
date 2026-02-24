#!/usr/bin/env python3
"""Trace through session service retrieval"""
from app.modules.file_uploads.repositories.file_repository import UploadSessionRepository
from app.modules.file_uploads.services.session_service import SessionService

session_id = 'test_sess_0a9cecdf'

print(f'Testing session: {session_id}')

# Step 1: Check expiration directly
is_expired = UploadSessionRepository.is_session_expired(session_id)
print(f'1. is_session_expired(): {is_expired}')

# Step 2: Try to get session directly
session = UploadSessionRepository.get_session(session_id)
print(f'2. get_session(): {session}')

# Step 3: Try with file count
session_with_count = UploadSessionRepository.get_session_with_file_count(session_id)
print(f'3. get_session_with_file_count(): {session_with_count}')

# Step 4: Try through service
service_session = SessionService.get_session(session_id)
print(f'4. SessionService.get_session(): {service_session}')
