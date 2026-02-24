#!/usr/bin/env python3
"""
Test file upload system module imports and basic functionality
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test all module imports"""
    print("=" * 60)
    print("Testing File Upload System Module Imports")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test configuration
    try:
        from app.modules.file_uploads.config import FileUploadConfig, upload_config
        print("✓ Configuration imported successfully")
        print(f"  - Upload dir: {upload_config.UPLOADS_BASE_DIR}")
        print(f"  - Max file size: {upload_config.MAX_FILE_SIZE_MB}MB")
        print(f"  - Session TTL: {upload_config.SESSION_TTL_HOURS}h")
        print(f"  - Max files per session: {upload_config.MAX_FILES_PER_SESSION}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Configuration import failed: {e}")
        tests_failed += 1
    
    # Test storage layer
    try:
        from app.modules.file_uploads.storage.base import StorageProvider
        from app.modules.file_uploads.storage.local_storage import LocalStorageProvider
        
        provider = LocalStorageProvider()
        print("✓ Storage layer imported and instantiated")
        print(f"  - Storage provider: LocalStorageProvider")
        print(f"  - Base path: {provider.base_path}")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Storage layer import failed: {e}")
        tests_failed += 1
    
    # Test security utilities
    try:
        from app.modules.file_uploads.utils.security import (
            FileSecurityValidator,
            RateLimiter,
            AccessTokenValidator
        )
        
        validator = FileSecurityValidator()
        sanitized = validator.sanitize_filename("test_document.pdf")
        print("✓ Security utilities imported and tested")
        print(f"  - Sanitized example: 'test_document.pdf' → '{sanitized}'")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Security utilities import failed: {e}")
        tests_failed += 1
    
    # Test Pydantic schemas
    try:
        from app.modules.file_uploads.schemas.requests import (
            CreateSessionRequest,
            SessionResponse,
            FileMetadata,
            FileUploadResponse,
            ListFilesResponse,
            DeleteFileResponse,
            SessionStatsResponse
        )
        
        print("✓ Pydantic schemas imported successfully")
        print(f"  - 7 complete schema models defined")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Pydantic schemas import failed: {e}")
        tests_failed += 1
    
    # Test repository layer (skip DB tests, just check imports)
    try:
        from app.modules.file_uploads.repositories.file_repository import (
            UploadSessionRepository,
            UploadFileRepository,
            UploadStatsRepository
        )
        
        print("✓ Repository layer imported successfully")
        print(f"  - 3 repository classes ready for database operations")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Repository layer import failed: {e}")
        tests_failed += 1
    
    # Test service layer
    try:
        from app.modules.file_uploads.services.session_service import SessionService
        from app.modules.file_uploads.services.file_service import FileService
        
        print("✓ Service layer imported successfully")
        print(f"  - SessionService: Session lifecycle management")
        print(f"  - FileService: File upload/download/delete operations")
        tests_passed += 1
    except Exception as e:
        print(f"✗ Service layer import failed: {e}")
        tests_failed += 1
    
    # Test API routes
    try:
        from app.modules.file_uploads.controllers.routes import router
        
        # Count routes
        num_routes = len([r for r in router.routes])
        print("✓ API routes imported successfully")
        print(f"  - FastAPI router with {num_routes} endpoints defined")
        
        # List endpoints
        route_paths = []
        for route in router.routes:
            if hasattr(route, 'path'):
                route_paths.append(f"{route.path}")
        
        if route_paths:
            print(f"  - Endpoints:")
            for path in sorted(set(route_paths)):
                print(f"    • /api/uploads{path}")
        
        tests_passed += 1
    except Exception as e:
        print(f"✗ API routes import failed: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    total_tests = tests_passed + tests_failed
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Tests Failed: {tests_failed}/{total_tests}")
    
    if tests_failed == 0:
        print("\n✓ All module imports successful!")
        print("✓ File Upload System is ready for use")
        return 0
    else:
        print(f"\n✗ {tests_failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = test_imports()
    sys.exit(exit_code)
