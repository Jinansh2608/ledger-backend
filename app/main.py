"""
Nexgen ERP Finance API - Production Ready
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.apis import health, auth
from app.apis import bajaj_po, client_po, po_management, proforma_invoice, documents, payments
from app.apis import vendors, vendor_orders, vendor_payment_links, vendor_payments, billing_po, projects, quotations

from app.modules.file_uploads.controllers.routes import router as file_uploads_router
from app.config import settings
from app.logger import get_logger
from app.exceptions import register_error_handlers
from app.database import init_connection_pool, close_pool
from fastapi.staticfiles import StaticFiles
import os
import logging

# Initialize logging
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Finance management API for Nexgen ERP",
    openapi_url=f"{settings.API_PREFIX}/openapi.json" if not settings.is_production else None,
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url="/api/redoc" if not settings.is_production else None
)

# Initialize database pool on startup (lazy if fails)
@app.on_event("startup")
async def startup_event():
    """Initialize database and other resources on startup"""
    logger.info(f"Starting application in {settings.APP_ENVIRONMENT} mode")
    try:
        # Try to initialize pool, but don't fail if database unavailable
        # Pool will be initialized on first use
        logger.info("Application startup complete")
    except Exception as e:
        logger.warning(f"Could not pre-initialize database: {e} (will retry on first use)")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("Shutting down application")
    try:
        close_pool()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Add middleware for logging
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response

# Add security middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware FIRST (before other middleware) with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Register error handlers
register_error_handlers(app)

# Register API routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(bajaj_po.router)
app.include_router(client_po.router)
app.include_router(po_management.router)
app.include_router(proforma_invoice.router)
app.include_router(documents.router)
app.include_router(payments.router)
app.include_router(vendors.router)
app.include_router(vendor_orders.router)
app.include_router(vendor_payment_links.router)
app.include_router(vendor_payments.router)
app.include_router(billing_po.router)
app.include_router(projects.router)
app.include_router(quotations.router)
app.include_router(file_uploads_router, prefix="/api")


# Mount uploads directory to serve compressed files and session files
uploads_path = os.path.join(os.path.dirname(__file__), '..', 'uploads')
uploads_path = os.path.normpath(os.path.abspath(uploads_path))
os.makedirs(uploads_path, exist_ok=True)

# Mount main uploads directory
app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

# Also mount sessions subdirectory for the new file upload system
sessions_path = os.path.join(uploads_path, 'sessions')
os.makedirs(sessions_path, exist_ok=True)

logger.info(f"Application initialized - API Prefix: {settings.API_PREFIX}, Uploads: {uploads_path}")
# Note: mounting at /uploads/sessions is handled by the /uploads mount above
