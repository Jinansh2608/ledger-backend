"""
Standard response models for all API endpoints
Ensures consistent response format across the application
"""
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
from datetime import datetime

class Error(BaseModel):
    """Error detail in validation error response"""
    field: str
    message: str
    type: str

class StandardErrorResponse(BaseModel):
    """Standard error response format"""
    status: str = "ERROR"
    error_code: str
    message: str
    path: str
    errors: Optional[List[Error]] = None

class StandardSuccessResponse(BaseModel):
    """Standard success response format"""
    status: str = "SUCCESS"
    message: Optional[str] = None
    data: Optional[Any] = None
    timestamp: datetime = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "message": "Operation completed successfully",
                "data": {}
            }
        }

class PaginatedResponse(BaseModel):
    """Paginated response format"""
    status: str = "SUCCESS"
    data: List[Any]
    total_count: int
    page: int
    page_size: int
    has_next: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "data": [],
                "total_count": 100,
                "page": 1,
                "page_size": 20,
                "has_next": True
            }
        }

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    database: str
    version: str
    timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "UP",
                "service": "Nexgen ERP - Finance",
                "database": "UP",
                "version": "1.0.0",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
# Authentication Schemas

class SignupRequest(BaseModel):
    """User signup request"""
    username: str
    email: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        }

class LoginRequest(BaseModel):
    """User login request"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure_password_123"
            }
        }

class UserResponse(BaseModel):
    """User data response (without password)"""
    user_id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class TokenResponse(BaseModel):
    """Token response after login/signup"""
    access_token: str
    token_type: str
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "user_id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "created_at": "2024-01-01T00:00:00Z"
                }
            }
        }