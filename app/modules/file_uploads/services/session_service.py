"""
Service layer for upload session management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.modules.file_uploads.repositories.file_repository import (
    UploadSessionRepository,
    UploadFileRepository,
    UploadStatsRepository
)
from app.modules.file_uploads.config import upload_config
import uuid
import hashlib


class SessionService:
    """Service for managing upload sessions"""
    
    @staticmethod
    def _generate_session_id(client_id: Optional[int] = None) -> str:
        """
        Generate a session ID with naming convention: client+timestamp
        Format: sess_[client_id]_[timestamp]_[short_hash]
        Example: sess_client1_20260211_143022_a7f2
        
        Args:
            client_id: Optional client ID for naming
            
        Returns:
            str: Generated session ID
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_hash = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:4]
        
        if client_id:
            return f"sess_client{client_id}_{timestamp}_{unique_hash}"
        else:
            return f"sess_generic_{timestamp}_{unique_hash}"
    
    @staticmethod
    def create_session(
        metadata: Dict[str, Any] = None,
        ttl_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new upload session
        
        Args:
            metadata: Optional metadata for the session
            ttl_hours: Time to live for the session in hours
            
        Returns:
            dict: Created session data
        """
        # Validate TTL
        if ttl_hours < 1 or ttl_hours > 730:  # 30 days max
            ttl_hours = upload_config.SESSION_TTL_HOURS
        
        # Extract client_id from metadata for session naming
        client_id = None
        if metadata and 'client_id' in metadata:
            client_id = metadata['client_id']
        
        # Generate session ID with naming convention
        session_id = SessionService._generate_session_id(client_id)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        
        # Create session in database
        session = UploadSessionRepository.create_session(
            session_id=session_id,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        return session
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            dict: Session data with file count
        """
        # Check expiration
        if UploadSessionRepository.is_session_expired(session_id):
            return None
        
        return UploadSessionRepository.get_session_with_file_count(session_id)
    
    @staticmethod
    def validate_session(session_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate session is active and not expired
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        session = UploadSessionRepository.get_session(session_id)
        
        if not session:
            return False, "Session not found"
        
        if session['status'] != 'active':
            return False, f"Session is {session['status']}"
        
        if session['expires_at'] < datetime.utcnow():
            return False, "Session has expired"
        
        return True, None
    
    @staticmethod
    def get_session_stats(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            dict: Session statistics
        """
        is_valid, _ = SessionService.validate_session(session_id)
        if not is_valid:
            return None
        
        file_count = UploadFileRepository.get_session_file_count(session_id)
        total_size = UploadFileRepository.get_session_total_size(session_id)
        stats = UploadStatsRepository.get_stats(session_id)
        
        return {
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_downloads": stats.get('total_downloads', 0) if stats else 0,
            "last_activity": stats.get('last_activity') if stats else None
        }
    
    @staticmethod
    def expire_session(session_id: str) -> bool:
        """
        Manually expire a session
        
        Args:
            session_id: Session ID to expire
            
        Returns:
            bool: True if successful
        """
        return UploadSessionRepository.update_session_status(session_id, 'expired')
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """
        Delete a session and all its files
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            bool: True if successful
        """
        return UploadSessionRepository.delete_session(session_id)
    
    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        Find and expire all expired sessions
        
        Returns:
            int: Number of sessions expired
        """
        # This would be called by a background task/cron job
        # Implementation would scan database and expire old sessions
        return 0
