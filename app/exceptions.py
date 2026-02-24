"""
Exception handlers and error middleware for production
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.logger import get_logger
from app.config import settings
import traceback

logger = get_logger(__name__)

class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(self.message)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, 400, "VALIDATION_ERROR")

class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message: str):
        super().__init__(message, 404, "NOT_FOUND")

class UnauthorizedError(APIError):
    """Unauthorized access error"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401, "UNAUTHORIZED")

class ForbiddenError(APIError):
    """Forbidden access error"""
    def __init__(self, message: str):
        super().__init__(message, 403, "FORBIDDEN")

def register_error_handlers(app: FastAPI):
    """Register all error handlers with the FastAPI app"""
    
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        """Handle custom API errors"""
        logger.warning(f"API Error: {exc.error_code} - {exc.message} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "ERROR",
                "error_code": exc.error_code,
                "message": exc.message,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} - Path: {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "ERROR",
                "error_code": "HTTP_ERROR",
                "message": exc.detail,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors"""
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(x) for x in error["loc"][1:]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(f"Validation Error: {len(errors)} errors in request to {request.url.path}")
        
        return JSONResponse(
            status_code=422,
            content={
                "status": "ERROR",
                "error_code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "errors": errors,
                "path": request.url.path
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions"""
        logger.error(f"Unhandled Exception: {type(exc).__name__} - {str(exc)}", exc_info=True)
        
        # In production, don't expose internal error details
        if settings.is_production:
            message = "An internal server error occurred"
        else:
            message = f"{type(exc).__name__}: {str(exc)}"
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "ERROR",
                "error_code": "INTERNAL_ERROR",
                "message": message,
                "path": request.url.path,
                "debug": settings.DEBUG_MODE
            }
        )
