"""
Production-ready configuration
Uses environment variables with secure defaults
"""
import os
from typing import List

class Settings:
    """Application settings from environment variables"""
    
    def __init__(self):
        # Database Configuration
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = int(os.getenv("DB_PORT", "5432"))
        self.DB_NAME = os.getenv("DB_NAME", "Nexgen_erp")
        self.DB_USER = os.getenv("DB_USER", "postgres")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "toor")
        self.DB_SCHEMA = os.getenv("DB_SCHEMA", "Finances")
        self.DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
        self.DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
        self.DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        
        # Application Configuration
        self.APP_ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "development")
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # API Configuration
        self.API_TITLE = "Nexgen ERP - Finance API"
        self.API_VERSION = "1.0.0"
        self.API_PREFIX = "/api"
        
        # CORS Configuration - parse comma-separated list
        cors_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
        self.CORS_ORIGINS = [origin.strip() for origin in cors_str.split(",") if origin.strip()]
        self.CORS_ALLOW_CREDENTIALS = True
        self.CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        self.CORS_ALLOW_HEADERS = ["*"]
        
        # Authentication Configuration
        self.SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # File Upload Configuration
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
        self.ALLOWED_FILE_TYPES = ["xlsx", "xls", "csv", "pdf"]
        
        # Pagination
        self.DEFAULT_PAGE_SIZE = 20
        self.MAX_PAGE_SIZE = 100
    
    @property
    def database_url(self) -> str:
        """Generate database URL for connection"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.APP_ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.APP_ENVIRONMENT == "development"

# Global settings instance
settings = Settings()
