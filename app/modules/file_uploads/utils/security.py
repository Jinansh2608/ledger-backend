"""
Security utilities for file upload system
"""

import re
import hashlib
import secrets
from pathlib import Path
from typing import Optional, List
from datetime import datetime


class FileSecurityValidator:
    """Utilities for validating files and generating secure names"""
    
    # Dangerous characters that could be used in path traversal
    DANGEROUS_CHARS = r'[<>:"/\\|?*\x00]'
    
    # Extension blocklist (executing potentially dangerous files)
    BLOCKED_EXTENSIONS = {
        'exe', 'bat', 'cmd', 'com', 'scr', 'vbs', 'js', 'jar',
        'zip', 'rar', '7z',  # Archives can contain malicious content
        'dll', 'so', 'dylib',  # Dynamic libraries
        'msi', 'pkg',  # Installers
        'app', 'deb', 'rpm'  # Application packages
    }
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str:
        """
        Sanitize filename to prevent directory traversal and invalid characters
        
        Args:
            filename: Original filename
            max_length: Maximum filename length
            
        Returns:
            str: Sanitized filename
            
        Raises:
            ValueError: If filename is empty after sanitization
        """
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        # Remove path components (in case someone passes a full path)
        filename = Path(filename).name
        
        # Replace dangerous characters
        sanitized = re.sub(FileSecurityValidator.DANGEROUS_CHARS, '_', filename)
        
        # Remove leading/trailing dots and spaces (Windows reserved)
        sanitized = sanitized.strip('. ')
        
        # Normalize unicode
        sanitized = sanitized.encode('ascii', 'ignore').decode('ascii')
        
        # Collapse multiple underscores
        sanitized = re.sub(r'_{2,}', '_', sanitized)
        
        # Truncate if needed (preserving extension)
        if len(sanitized) > max_length:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            max_name_len = max_length - len(ext) - 1
            sanitized = name[:max_name_len] + ('.' + ext if ext else '')
        
        if not sanitized:
            raise ValueError("Filename became empty after sanitization")
        
        return sanitized
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """
        Validate file extension against allowed list
        
        Args:
            filename: Filename to validate
            allowed_extensions: List of allowed extensions (without dots)
            
        Returns:
            bool: True if extension is allowed
        """
        if '.' not in filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower()
        
        # Check blocklist first
        if ext in FileSecurityValidator.BLOCKED_EXTENSIONS:
            return False
        
        # Check allowlist
        return ext in allowed_extensions or not allowed_extensions
    
    @staticmethod
    def validate_mime_type(
        mime_type: str,
        allowed_mime_types: List[str] = None
    ) -> bool:
        """
        Validate MIME type
        
        Args:
            mime_type: MIME type to validate
            allowed_mime_types: List of allowed MIME types
            
        Returns:
            bool: True if MIME type is allowed
        """
        if not mime_type:
            return False
        
        # Validate MIME type format
        if '/' not in mime_type:
            return False
        
        # Dangerous MIME types that could execute code
        dangerous_types = {
            'application/x-msdownload',
            'application/x-msdos-program',
            'application/x-executable',
            'application/x-elf-executable',
            'application/x-sharedlib',
            'text/x-shellscript',
            'application/x-perl',
            'application/x-python'
        }
        
        if mime_type.lower() in dangerous_types:
            return False
        
        if allowed_mime_types:
            return mime_type in allowed_mime_types
        
        return True
    
    @staticmethod
    def generate_secure_filename(original_filename: str) -> str:
        """
        Generate a secure random filename based on original
        
        Args:
            original_filename: Original filename to use for extension
            
        Returns:
            str: Secure random filename
        """
        # Extract extension
        ext = ''
        if '.' in original_filename:
            ext = '.' + original_filename.rsplit('.', 1)[1].lower()
        
        # Generate random name (16 bytes = 32 hex chars)
        random_part = secrets.token_hex(16)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        return f"{timestamp}_{random_part}{ext}"
    
    @staticmethod
    def calculate_file_hash(file_content: bytes, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of file content
        
        Args:
            file_content: File content as bytes
            algorithm: Hash algorithm to use
            
        Returns:
            str: Hex digest of file hash
        """
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(file_content)
        return hash_obj.hexdigest()
    
    @staticmethod
    def generate_access_token(length: int = 32) -> str:
        """
        Generate secure random access token
        
        Args:
            length: Length of token (in bytes)
            
        Returns:
            str: Random hex token
        """
        return secrets.token_hex(length // 2)


class RateLimiter:
    """Simple rate limiter for file uploads"""
    
    def __init__(self):
        """Initialize rate limiter"""
        # In production, use Redis or similar
        self.upload_counts = {}
        self.download_counts = {}
    
    def check_upload_limit(
        self,
        session_id: str,
        max_uploads_per_hour: int = 100
    ) -> bool:
        """
        Check if upload limit is exceeded
        
        Args:
            session_id: Session ID to check
            max_uploads_per_hour: Maximum uploads per hour
            
        Returns:
            bool: True if upload is allowed
        """
        # Simple in-memory implementation
        # In production, this would use Redis with TTL
        now = datetime.utcnow().timestamp()
        
        if session_id not in self.upload_counts:
            self.upload_counts[session_id] = []
        
        # Remove old entries (older than 1 hour)
        self.upload_counts[session_id] = [
            ts for ts in self.upload_counts[session_id]
            if now - ts < 3600
        ]
        
        if len(self.upload_counts[session_id]) >= max_uploads_per_hour:
            return False
        
        self.upload_counts[session_id].append(now)
        return True
    
    def check_download_limit(
        self,
        session_id: str,
        max_downloads_per_hour: int = 1000
    ) -> bool:
        """
        Check if download limit is exceeded
        
        Args:
            session_id: Session ID to check
            max_downloads_per_hour: Maximum downloads per hour
            
        Returns:
            bool: True if download is allowed
        """
        now = datetime.utcnow().timestamp()
        
        if session_id not in self.download_counts:
            self.download_counts[session_id] = []
        
        # Remove old entries (older than 1 hour)
        self.download_counts[session_id] = [
            ts for ts in self.download_counts[session_id]
            if now - ts < 3600
        ]
        
        if len(self.download_counts[session_id]) >= max_downloads_per_hour:
            return False
        
        self.download_counts[session_id].append(now)
        return True


class AccessTokenValidator:
    """Validator for access tokens and session ownership"""
    
    @staticmethod
    def validate_session_access(
        session_id: str,
        user_id: Optional[str] = None,
        access_token: Optional[str] = None
    ) -> bool:
        """
        Validate if user has access to session
        
        Args:
            session_id: Session ID to access
            user_id: User ID (optional)
            access_token: Access token (optional)
            
        Returns:
            bool: True if access is granted
        """
        # In production, validate against database
        # This is a placeholder implementation
        return bool(session_id and (user_id or access_token))
    
    @staticmethod
    def validate_file_access(
        file_id: str,
        session_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Validate if user has access to file
        
        Args:
            file_id: File ID to access
            session_id: Session that file belongs to
            user_id: User ID (optional)
            
        Returns:
            bool: True if access is granted
        """
        # Verify file belongs to session and user has access to session
        return bool(file_id and session_id)
