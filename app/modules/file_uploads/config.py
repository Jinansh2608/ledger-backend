"""
File Upload Configuration
"""

from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class FileUploadConfig:
    """Configuration for file upload system"""
    
    # Storage paths
    UPLOADS_BASE_DIR: Path = Path(os.path.join(os.path.dirname(__file__), '../../..', 'uploads', 'sessions'))
    TEMP_DIR: Path = Path(os.path.join(os.path.dirname(__file__), '../../..', 'uploads', 'temp'))
    
    # Session configuration
    SESSION_TTL_HOURS: int = 24  # Session expiration time
    SESSION_ID_PREFIX: str = "sess_"
    
    # File upload limits
    MAX_FILE_SIZE_MB: int = 100  # Max file size in MB
    MAX_FILES_PER_SESSION: int = 50  # Max files in a session
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS: set = None
    
    # Allowed file types (MIME types)
    ALLOWED_MIME_TYPES: set = None
    
    # File naming
    SANITIZE_FILENAMES: bool = True
    PRESERVE_ORIGINAL_NAMES: bool = True  # Keep a record of original names
    
    # Rate limiting
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_UPLOADS_PER_HOUR: int = 100  # Per session
    
    # Security
    VIRUS_SCAN_ENABLED: bool = False  # ClamAV integration (optional)
    REQUIRE_AUTH: bool = True  # Require authentication for uploads
    
    # URL configuration
    FILE_ACCESS_URL_BASE: str = "/api/uploads/files"
    DOWNLOAD_ENABLE: bool = True
    PREVIEW_ENABLE: bool = True
    
    def __post_init__(self):
        """Initialize defaults after dataclass creation"""
        if self.ALLOWED_EXTENSIONS is None:
            self.ALLOWED_EXTENSIONS = {
                # Documents
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                'txt', 'csv', 'rtf',
                
                # Images
                'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'ico',
                
                # Archives
                'zip', 'rar', '7z', 'gz', 'tar',
                
                # Code
                'json', 'xml', 'yaml', 'yml', 'html', 'css', 'js',
            }
        
        if self.ALLOWED_MIME_TYPES is None:
            self.ALLOWED_MIME_TYPES = {
                # Documents
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'text/plain',
                'text/csv',
                
                # Images
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/webp',
                'image/svg+xml',
                
                # Archives
                'application/zip',
                'application/x-rar-compressed',
                'application/x-7z-compressed',
                'application/gzip',
            }
        
        # Create directories if they don't exist
        self.UPLOADS_BASE_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        
        # Convert MB to bytes for easier use in file_service
        self.MAX_FILE_SIZE_BYTES = self.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes
        
        # Add rate limit for downloads if not set
        if not hasattr(self, 'RATE_LIMIT_DOWNLOADS_PER_HOUR'):
            self.RATE_LIMIT_DOWNLOADS_PER_HOUR = 1000  # Per session


# Global configuration instance
upload_config = FileUploadConfig()
