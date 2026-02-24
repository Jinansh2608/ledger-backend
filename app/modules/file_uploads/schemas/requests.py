"""
Pydantic schemas for file upload system
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

class CreateSessionRequest(BaseModel):
    """Request to create a new upload session"""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session metadata")
    ttl_hours: Optional[int] = Field(default=24, ge=1, le=720, description="Session TTL in hours")
    client_id: Optional[int] = Field(default=None, description="Client ID (optional for backward compatibility)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {"project": "nexgen", "user": "john_doe"},
                "ttl_hours": 24,
                "client_id": 1
            }
        }


class CreateClientSessionRequest(BaseModel):
    """Request to create a new upload session with mandatory client_id"""
    client_id: int = Field(..., ge=1, description="Client ID (Bajaj=1, Dava India=2)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session metadata")
    ttl_hours: Optional[int] = Field(default=24, ge=1, le=720, description="Session TTL in hours")
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": 1,
                "metadata": {"project": "nexgen", "user": "john_doe"},
                "ttl_hours": 24
            }
        }


class ParsedPOResponse(BaseModel):
    """Response after successful file parsing"""
    status: str = "SUCCESS"
    file_id: str
    session_id: str
    client_id: int
    client_name: str
    parser_type: str
    po_details: Dict[str, Any]
    line_items: List[Dict[str, Any]]
    line_item_count: int
    client_po_id: Optional[int] = None
    project_name: Optional[str] = None
    project_id: Optional[int] = None
    original_filename: str
    upload_timestamp: datetime
    dashboard_info: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "file_id": "file_xyz789",
                "session_id": "sess_abc123def456",
                "client_id": 1,
                "client_name": "Bajaj",
                "parser_type": "po",
                "project_name": "Project A",
                "project_id": 1,
                "po_details": {
                    "po_number": "123456",
                    "po_date": "2026-02-10"
                },
                "line_items": [],
                "line_item_count": 0,
                "original_filename": "Bajaj_PO.xlsx",
                "upload_timestamp": "2026-02-10T10:30:00Z",
                "dashboard_info": {
                    "project_name": "Project A",
                    "po_number": "123456",
                    "client_po_id": 1,
                    "line_items_count": 0
                }
            }
        }


class SessionResponse(BaseModel):
    """Response containing session information"""
    session_id: str
    created_at: datetime
    expires_at: datetime
    status: str
    metadata: Dict[str, Any]
    file_count: Optional[int] = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123def456",
                "created_at": "2026-02-09T10:00:00Z",
                "expires_at": "2026-02-10T10:00:00Z",
                "status": "active",
                "metadata": {"project": "nexgen"},
                "file_count": 3
            }
        }


class FileMetadata(BaseModel):
    """File metadata information"""
    id: str
    session_id: str
    original_filename: str
    storage_filename: str
    file_size: int
    mime_type: Optional[str]
    file_hash: Optional[str]
    upload_timestamp: datetime
    uploaded_by: Optional[str]
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "file_xyz789",
                "session_id": "sess_abc123def456",
                "original_filename": "report.pdf",
                "storage_filename": "xyz789_report.pdf",
                "file_size": 1024000,
                "mime_type": "application/pdf",
                "file_hash": "sha256hash...",
                "upload_timestamp": "2026-02-09T10:30:00Z",
                "uploaded_by": "john_doe",
                "status": "active"
            }
        }


class FileUploadResponse(BaseModel):
    """Response after successful file upload"""
    status: str = "SUCCESS"
    file_id: str
    session_id: str
    original_filename: str
    file_size: int
    compressed_size: Optional[int] = None
    is_compressed: bool = True
    mime_type: Optional[str] = None
    original_mime_type: Optional[str] = None
    file_hash: Optional[str] = None
    compressed_hash: Optional[str] = None
    upload_timestamp: datetime
    po_number: Optional[str] = None
    access_url: str
    direct_url: Optional[str] = None
    # Parsing status fields
    parse_status: Optional[str] = None  # "SUCCESS", "SKIPPED", "FAILED"
    parse_error: Optional[str] = None  # Error message if parse failed
    po_id: Optional[int] = None  # ID of created PO if successful
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "file_id": "file_xyz789",
                "session_id": "sess_abc123def456",
                "original_filename": "report.pdf",
                "file_size": 1024000,
                "mime_type": "application/pdf",
                "file_hash": "sha256hash...",
                "upload_timestamp": "2026-02-09T10:30:00Z",
                "access_url": "/api/uploads/files/file_xyz789",
                "direct_url": "/uploads/sess_abc123def456/file_xyz789.pdf",
                "parse_status": "SUCCESS",
                "po_id": 112
            }
        }


class ListFilesResponse(BaseModel):
    """Response containing list of files for a session"""
    status: str = "SUCCESS"
    session_id: str
    file_count: int
    total_size: int
    files: List[FileMetadata]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "session_id": "sess_abc123def456",
                "file_count": 2,
                "total_size": 2048000,
                "files": []
            }
        }


class POFilesResponse(BaseModel):
    """Response containing list of files for a PO number"""
    status: str = "SUCCESS"
    po_number: str
    file_count: int
    total_size: int
    compressed_size: int = 0
    compression_ratio: float = 0.0
    files: List[FileMetadata] = Field(default_factory=list)
    skip: int = 0
    limit: int = 50
    total_count: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "po_number": "PO-2026-001",
                "file_count": 2,
                "total_size": 2048000,
                "compressed_size": 512000,
                "compression_ratio": 75.0,
                "files": [],
                "skip": 0,
                "limit": 50,
                "total_count": 2
            }
        }


class DeleteFileRequest(BaseModel):
    """Request to delete a file"""
    reason: Optional[str] = Field(default="user_request", description="Reason for deletion")


class DeleteFileResponse(BaseModel):
    """Response after deleting a file"""
    status: str = "SUCCESS"
    message: str
    file_id: str
    session_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "message": "File deleted successfully",
                "file_id": "file_xyz789",
                "session_id": "sess_abc123def456"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "ERROR"
    error_code: str
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ERROR",
                "error_code": "SESSION_NOT_FOUND",
                "message": "Upload session not found",
                "detail": "Session ID 'sess_unknown' does not exist",
                "timestamp": "2026-02-09T10:30:00Z"
            }
        }


class FileValidationError(BaseModel):
    """File validation error details"""
    field: str
    error: str
    value: Optional[Any] = None


class ValidationErrorResponse(BaseModel):
    """Response for validation errors"""
    status: str = "VALIDATION_ERROR"
    message: str
    errors: List[FileValidationError]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "VALIDATION_ERROR",
                "message": "File validation failed",
                "errors": [
                    {
                        "field": "file_size",
                        "error": "File size exceeds 100MB limit",
                        "value": 150000000
                    }
                ]
            }
        }


class SessionStatsResponse(BaseModel):
    """Session statistics"""
    session_id: str
    total_files: int
    total_size_bytes: int
    total_downloads: int
    created_at: datetime
    expires_at: datetime
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess_abc123def456",
                "total_files": 5,
                "total_size_bytes": 5242880,
                "total_downloads": 12,
                "created_at": "2026-02-09T10:00:00Z",
                "expires_at": "2026-02-10T10:00:00Z",
                "status": "active"
            }
        }
