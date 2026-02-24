"""
Health check endpoints for system monitoring
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.database import get_db
from app.schemas import HealthCheckResponse
from app.logger import get_logger
from app.config import settings

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health", response_model=HealthCheckResponse)
def health_check():
    """
    Health check endpoint for the Finance API
    Returns status of the API and database connectivity
    """
    db_status = "DOWN"
    
    try:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            db_status = "UP"
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "DOWN"

    return HealthCheckResponse(
        status="UP" if db_status == "UP" else "DEGRADED",
        service=settings.API_TITLE,
        database=db_status,
        version=settings.API_VERSION,
        timestamp=datetime.utcnow()
    )

@router.get("/health/detailed")
def detailed_health_check():
    """
    Detailed health check with additional metrics
    For monitoring and debugging purposes
    """
    health_info = {
        "status": "UP",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "environment": settings.APP_ENVIRONMENT,
        "components": {
            "api": "UP",
            "database": "DOWN"
        }
    }
    
    # Check database
    try:
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = %s", 
                           (settings.DB_SCHEMA,))
                result = cur.fetchone()
                table_count = result['table_count'] if isinstance(result, dict) else result[0]
            
            health_info["components"]["database"] = "UP"
            health_info["database_tables"] = table_count
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"Detailed health check - database check failed: {e}")
        health_info["components"]["database"] = "DOWN"
        health_info["status"] = "DEGRADED"
    
    return health_info

