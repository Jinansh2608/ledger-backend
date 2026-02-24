import uvicorn
import sys
import os
import logging
from pathlib import Path

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Set up console logging before starting uvicorn
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def print_startup_info():
    """Print startup information"""
    print("\n" + "="*70)
    print("  >> NexGen Finance API - Starting")
    print("="*70)
    print(f"  Port:        http://localhost:8000")
    print(f"  API Docs:    http://localhost:8000/api/docs")
    print(f"  API Redoc:   http://localhost:8000/api/redoc")
    print(f"  Live Logs:   logs/app.log (rotated max 10MB)")
    print(f"  Error Logs:  logs/error.log (rotated max 10MB)")
    print(f"  Console:     Shows INFO level and above")
    print("="*70)
    print("\n[*] API Endpoints Available:")
    print("  • GET  /api/health              - Health check")
    print("  • GET  /api/projects            - List projects")
    print("  • GET  /api/vendors             - List vendors")
    print("  • POST /api/projects            - Create project")
    print("  • POST /api/vendors             - Create vendor")
    print("\n[+] View all endpoints at: http://localhost:8000/api/docs\n")

if __name__ == "__main__":
    # Check for verbose flag
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    # Remove custom flags before passing to uvicorn
    sys.argv = [arg for arg in sys.argv if arg not in ["--verbose", "-v"]]
    
    print_startup_info()
    
    logger.info("Starting Uvicorn server...")
    logger.info("Press Ctrl+C to stop the server")
    logger.info(f"Verbose mode: {'ON' if verbose else 'OFF'}")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="debug" if verbose else "info",
            access_log=True,  # Enable access logs
            use_colors=True   # Use colored output
        )
    except KeyboardInterrupt:
        logger.info("\n[X] Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"[ERROR] Server error: {e}", exc_info=True)
        sys.exit(1)
