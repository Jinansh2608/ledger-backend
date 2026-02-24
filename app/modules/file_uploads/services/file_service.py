"""
Service layer for file upload management
"""

from typing import Optional, BinaryIO, Dict, Any, List, Tuple
from pathlib import Path
import uuid
import gzip
import io
import hashlib
from app.modules.file_uploads.repositories.file_repository import (
    UploadFileRepository,
    UploadStatsRepository
)
from app.modules.file_uploads.storage.local_storage import LocalStorageProvider
from app.modules.file_uploads.utils.security import (
    FileSecurityValidator,
    RateLimiter,
    AccessTokenValidator
)
from app.modules.file_uploads.config import upload_config
from .session_service import SessionService


class FileService:
    """Service for managing file uploads and downloads"""
    
    def __init__(self):
        """Initialize file service"""
        self.storage = LocalStorageProvider()
        self.rate_limiter = RateLimiter()
        self.validator = FileSecurityValidator()
    
    def upload_file(
        self,
        session_id: str,
        file_content: BinaryIO,
        original_filename: str,
        uploaded_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        po_number: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Upload a file to a session with automatic compression
        
        Args:
            session_id: Target session ID
            file_content: File object to upload
            original_filename: Original filename
            uploaded_by: User who uploaded (optional)
            metadata: Additional metadata (optional)
            po_number: Purchase Order number (optional)
            
        Returns:
            dict: Uploaded file metadata
        """
        # Validate session
        is_valid, error = SessionService.validate_session(session_id)
        if not is_valid:
            raise ValueError(f"Invalid session: {error}")
        
        # Check rate limit
        if not self.rate_limiter.check_upload_limit(
            session_id,
            upload_config.RATE_LIMIT_UPLOADS_PER_HOUR
        ):
            raise ValueError("Upload rate limit exceeded")
        
        # Check file count limit
        file_count = UploadFileRepository.get_session_file_count(session_id)
        if file_count >= upload_config.MAX_FILES_PER_SESSION:
            raise ValueError(f"Session file limit ({upload_config.MAX_FILES_PER_SESSION}) exceeded")
        
        # Validate file size
        file_content.seek(0, 2)  # Seek to end
        file_size = file_content.tell()
        file_content.seek(0)  # Reset to beginning
        
        if file_size > upload_config.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size ({file_size} bytes) exceeds limit "
                f"({upload_config.MAX_FILE_SIZE_BYTES} bytes)"
            )
        
        # Sanitize filename
        try:
            sanitized_filename = self.validator.sanitize_filename(original_filename)
        except ValueError as e:
            raise ValueError(f"Invalid filename: {e}")
        
        # Validate extension
        if not self.validator.validate_file_extension(
            sanitized_filename,
            [ext.lstrip('.') for ext in upload_config.ALLOWED_EXTENSIONS]
        ):
            raise ValueError(f"File extension not allowed")
        
        # Determine MIME type from filename
        # In production, use python-magic or similar
        original_mime_type = self._guess_mime_type(original_filename)
        
        # Validate MIME type
        if not self.validator.validate_mime_type(
            original_mime_type,
            list(upload_config.ALLOWED_MIME_TYPES)
        ):
            raise ValueError(f"File type not allowed")
        
        # Generate secure storage filename
        secure_filename = self.validator.generate_secure_filename(sanitized_filename)
        
        # Calculate original file hash
        file_content.seek(0)
        original_content = file_content.read()
        file_hash = self.validator.calculate_file_hash(original_content)
        file_content.seek(0)
        
        # Compress file
        compressed_content, compressed_size, is_compressed, compressed_hash = self._compress_file(
            original_content, format='gzip'
        )
        
        # Save compressed file to storage
        storage_path = f"{session_id}"
        content_to_save = io.BytesIO(compressed_content)
        if not self.storage.save_file(content_to_save, storage_path, secure_filename):
            raise ValueError("Failed to save file to storage")
        
        # Save metadata to database
        file_metadata = UploadFileRepository.create_file(
            session_id=session_id,
            po_number=po_number,
            original_filename=sanitized_filename,
            storage_filename=secure_filename,
            storage_path=storage_path,
            file_size=file_size,
            compressed_size=compressed_size,
            is_compressed=is_compressed,
            mime_type='application/gzip' if is_compressed else original_mime_type,
            original_mime_type=original_mime_type,
            file_hash=file_hash,
            compressed_hash=compressed_hash,
            uploaded_by=uploaded_by,
            metadata=metadata or {}
        )
        
        return file_metadata
    
    def download_file(
        self,
        file_id: str,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Download a file
        
        Args:
            file_id: File ID to download
            session_id: Session ID (for validation)
            user_id: Optional user ID for access control
            
        Returns:
            bytes: File content
        """
        # Validate access
        if not AccessTokenValidator.validate_file_access(file_id, session_id, user_id):
            raise ValueError("Access denied to file")
        
        # Check rate limit
        if not self.rate_limiter.check_download_limit(
            session_id,
            upload_config.RATE_LIMIT_DOWNLOADS_PER_HOUR
        ):
            raise ValueError("Download rate limit exceeded")
        
        # Get file metadata
        file_data = UploadFileRepository.get_file_if_belongs_to_session(file_id, session_id)
        if not file_data:
            raise ValueError("File not found or does not belong to session")
        
        # Get file from storage
        file_content = self.storage.get_file(
            file_data['storage_path'],
            file_data['storage_filename']
        )
        
        if file_content is None:
            raise ValueError("File not found in storage")
        
        # Decompress if needed
        is_compressed = file_data.get('is_compressed', False)
        decompressed_content = self._decompress_file(file_content, is_compressed)
        
        # Increment download count
        UploadStatsRepository.increment_download_count(session_id)
        
        return decompressed_content
    
    def delete_file(
        self,
        file_id: str,
        session_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Delete a file
        
        Args:
            file_id: File ID to delete
            session_id: Session ID (for validation)
            user_id: Optional user ID for access control
            
        Returns:
            bool: True if successful
        """
        # Validate access
        if not AccessTokenValidator.validate_file_access(file_id, session_id, user_id):
            raise ValueError("Access denied to file")
        
        # Get file metadata
        file_data = UploadFileRepository.get_file_if_belongs_to_session(file_id, session_id)
        if not file_data:
            raise ValueError("File not found")
        
        # Delete from storage
        self.storage.delete_file(
            file_data['storage_path'],
            file_data['storage_filename']
        )
        
        # Mark as deleted in database
        UploadFileRepository.delete_file(file_id, soft_delete=True)
        
        return True
    
    def list_session_files(session_id: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all files in a session
        
        Args:
            session_id: Session ID
            user_id: Optional user ID for access control
            
        Returns:
            list: List of file metadata
        """
        # Validate session exists and user has access
        session = SessionService.get_session(session_id)
        if not session:
            raise ValueError("Session not found or expired")
        
        files = UploadFileRepository.get_session_files(session_id, include_deleted=False)
        return files or []
    
    def generate_access_url(
        self,
        file_id: str,
        session_id: str,
        base_url: str = "https://api.example.com"
    ) -> str:
        """
        Generate a secure download URL for a file
        
        Args:
            file_id: File ID
            session_id: Session ID
            base_url: API base URL
            
        Returns:
            str: Download URL
        """
        # Generate access token
        access_token = self.validator.generate_access_token()
        
        # URL would be: {base_url}/api/uploads/{session_id}/files/{file_id}/download?token={access_token}
        # Token validation would happen at the endpoint
        
        return f"{base_url}/api/uploads/{session_id}/files/{file_id}/download?token={access_token}"
    
    def get_files_by_po_number(self, po_number: str) -> List[Dict[str, Any]]:
        """
        Get all files associated with a specific PO number
        
        Args:
            po_number: Purchase Order number
            
        Returns:
            list: List of file metadata for the PO
        """
        files = UploadFileRepository.get_files_by_po_number(po_number, include_deleted=False)
        return files or []
    
    def get_po_statistics(self, po_number: str) -> Dict[str, Any]:
        """
        Get statistics for all files associated with a PO number
        
        Args:
            po_number: Purchase Order number
            
        Returns:
            dict: Statistics including file count, sizes, compression ratio
        """
        file_count = UploadFileRepository.get_file_count_by_po(po_number)
        total_size = UploadFileRepository.get_total_size_by_po(po_number)
        compressed_size = UploadFileRepository.get_total_compressed_size_by_po(po_number)
        
        space_saved = total_size - compressed_size
        compression_ratio = ((total_size - compressed_size) / total_size * 100) if total_size > 0 else 0
        
        return {
            "po_number": po_number,
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_compressed_size": compressed_size,
            "space_saved_bytes": space_saved,
            "compression_ratio": round(compression_ratio, 2)
        }
    
    def get_file_by_po_and_id(self, po_number: str, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific file by PO number and file ID
        
        Args:
            po_number: Purchase Order number
            file_id: File ID
            
        Returns:
            dict: File metadata if found
        """
        files = UploadFileRepository.get_files_by_po_number(po_number)
        for file in files:
            if file.get('id') == file_id:
                return file
        return None
    
    def download_file_by_po(self, po_number: str, file_id: str) -> Optional[bytes]:
        """
        Download a file by PO number and file ID
        
        Args:
            po_number: Purchase Order number
            file_id: File ID
            
        Returns:
            bytes: File content
        """
        file_data = self.get_file_by_po_and_id(po_number, file_id)
        if not file_data:
            raise ValueError("File not found for this PO number")
        
        # Get file from storage
        file_content = self.storage.get_file(
            file_data['storage_path'],
            file_data['storage_filename']
        )
        
        if file_content is None:
            raise ValueError("File not found in storage")
        
        # Decompress if needed
        is_compressed = file_data.get('is_compressed', False)
        decompressed_content = self._decompress_file(file_content, is_compressed)
        
        # Increment download count
        UploadStatsRepository.increment_download_count(
            file_data.get('session_id', '')
        )
        
        return decompressed_content
    
    def delete_file_by_po(self, po_number: str, file_id: str) -> bool:
        """
        Delete a file by PO number and file ID
        
        Args:
            po_number: Purchase Order number
            file_id: File ID
            
        Returns:
            bool: True if successful
        """
        file_data = self.get_file_by_po_and_id(po_number, file_id)
        if not file_data:
            raise ValueError("File not found for this PO number")
        
        # Delete from storage
        self.storage.delete_file(
            file_data['storage_path'],
            file_data['storage_filename']
        )
        
        # Mark as deleted in database
        UploadFileRepository.delete_file(file_id, soft_delete=True)
        
        return True
    
    @staticmethod
    def _compress_file(
        file_content: bytes,
        format: str = 'gzip',
        compression_level: int = 6
    ) -> Tuple[bytes, int, bool, str]:
        """
        Compress file content using gzip
        
        Args:
            file_content: Original file content as bytes
            format: Compression format ('gzip' by default)
            compression_level: Compression level (1-9, default 6)
            
        Returns:
            Tuple[compressed_bytes, compressed_size, is_compressed, compressed_hash]
        """
        try:
            if format == 'gzip':
                # Compress with gzip
                compressed_buffer = io.BytesIO()
                with gzip.GzipFile(fileobj=compressed_buffer, mode='wb', compresslevel=compression_level) as gz:
                    gz.write(file_content)
                
                compressed_data = compressed_buffer.getvalue()
                compressed_size = len(compressed_data)
                
                # Calculate compression ratio
                original_size = len(file_content)
                compression_ratio = (1 - (compressed_size / original_size)) * 100 if original_size > 0 else 0
                
                # Only use compression if it saves space (>10% reduction)
                if compression_ratio > 10:
                    compressed_hash = hashlib.sha256(compressed_data).hexdigest()
                    return compressed_data, compressed_size, True, compressed_hash
                else:
                    # Return uncompressed if compression doesn't help
                    original_hash = hashlib.sha256(file_content).hexdigest()
                    return file_content, original_size, False, original_hash
            else:
                # Unsupported format, return original
                original_hash = hashlib.sha256(file_content).hexdigest()
                return file_content, len(file_content), False, original_hash
                
        except Exception as e:
            # If compression fails, return original file
            print(f"Compression error: {e}")
            original_hash = hashlib.sha256(file_content).hexdigest()
            return file_content, len(file_content), False, original_hash
    
    @staticmethod
    def _decompress_file(file_content: bytes, is_compressed: bool) -> bytes:
        """
        Decompress file content if it was compressed
        
        Args:
            file_content: File content (possibly compressed)
            is_compressed: Flag indicating if file was compressed
            
        Returns:
            bytes: Decompressed file content
        """
        if not is_compressed:
            return file_content
        
        try:
            # Decompress gzip
            compressed_buffer = io.BytesIO(file_content)
            with gzip.GzipFile(fileobj=compressed_buffer, mode='rb') as gz:
                return gz.read()
        except Exception as e:
            print(f"Decompression error: {e}")
            # Return original if decompression fails
            return file_content
    
    @staticmethod
    def _guess_mime_type(filename: str) -> str:
        """
        Guess MIME type from filename extension
        
        Args:
            filename: Filename
            
        Returns:
            str: MIME type
        """
        extension_map = {
            'pdf': 'application/pdf',
            'txt': 'text/plain',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'zip': 'application/zip',
            'csv': 'text/csv',
        }
        
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1].lower()
            return extension_map.get(ext, 'application/octet-stream')
        
        return 'application/octet-stream'
