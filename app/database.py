"""
Database connection management with pooling for production
Uses ThreadedConnectionPool for better thread safety
"""
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from app.config import settings
import logging
import atexit
import threading

logger = logging.getLogger(__name__)

# Connection pool for production
_connection_pool = None
_pool_lock = threading.Lock()

def init_connection_pool():
    """Initialize database connection pool"""
    global _connection_pool
    
    with _pool_lock:
        if _connection_pool:
            return  # Already initialized
        
        try:
            _connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=settings.DB_POOL_SIZE // 2,
                maxconn=settings.DB_POOL_SIZE,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                cursor_factory=RealDictCursor,
                connect_timeout=settings.DB_POOL_TIMEOUT,
                # Keep connections alive
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5,
                # Disable TCP_NODELAY for better batching
                tcp_user_timeout=30000
            )
            logger.info(f"Database connection pool initialized: {settings.DB_POOL_SIZE // 2}-{settings.DB_POOL_SIZE} connections")
            # Register cleanup on exit
            atexit.register(close_pool)
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

def get_db():
    """
    Get a database connection from the pool.
    Uses ThreadedConnectionPool for better safety.
    Must be used with context manager or close() must be called.
    """
    global _connection_pool
    
    if not _connection_pool:
        init_connection_pool()
    
    try:
        conn = _connection_pool.getconn()
        
        # Check if connection is working
        if conn.closed:
            logger.warning("Got closed connection from pool, creating new one")
            _connection_pool.putconn(conn, close=True)
            conn = _connection_pool.getconn()
        
        # Reset connection state
        try:
            with conn.cursor() as cur:
                # Clear any previous transaction state
                cur.execute('ROLLBACK')
                # Set schema
                cur.execute(f'SET search_path TO "{settings.DB_SCHEMA}";')
            conn.commit()
        except Exception as e:
            logger.warning(f"Error resetting connection: {e}")
            conn.rollback()
        
        # Return a wrapped connection that knows about the pool
        return PooledConnection(conn, _connection_pool)
    except pool.PoolError as e:
        logger.error(f"Connection pool exhausted: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        raise

def close_pool():
    """Close all connections in the pool (call on app shutdown)"""
    global _connection_pool
    with _pool_lock:
        if _connection_pool:
            try:
                _connection_pool.closeall()
                _connection_pool = None
                logger.info("Database connection pool closed")
            except Exception as e:
                logger.error(f"Error closing connection pool: {e}")

class PooledConnection:
    """
    Wrapper for psycopg2 connections obtained from ThreadedConnectionPool.
    Ensures proper return to pool when closed.
    """
    
    def __init__(self, real_conn, pool_ref):
        self._real_conn = real_conn
        self._pool = pool_ref
        self._closed = False
    
    def __getattr__(self, name):
        """Delegate all attribute access to the real connection"""
        if self._closed:
            raise psycopg2.OperationalError("Connection is closed")
        return getattr(self._real_conn, name)
    
    def close(self):
        """Return connection to pool instead of closing it"""
        if self._closed:
            return
        
        self._closed = True  # Mark as closed immediately to prevent double-calls
        
        if not self._real_conn or not self._pool:
            return
        
        try:
            # NOTE: Do NOT call rollback() here!
            # The __exit__ method already handles commit/rollback appropriately.
            # Calling rollback() here would undo committed transactions.
            
            # Return to pool - ThreadedConnectionPool handles this properly
            self._pool.putconn(self._real_conn, close=False)
        except psycopg2.OperationalError as e:
            # Connection is broken, close it
            logger.warning(f"Connection broken, closing instead of returning to pool: {e}")
            try:
                self._real_conn.close()
            except:
                pass
        except Exception as e:
            # Any other error, try to close the connection
            logger.error(f"Error returning connection to pool, closing instead: {e}")
            try:
                self._real_conn.close()
            except:
                pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            try:
                self._real_conn.rollback()
            except:
                pass
        else:
            # Commit if no exception occurred
            try:
                self._real_conn.commit()
            except:
                pass
        self.close()
    
    def cursor(self, *args, **kwargs):
        """Create a cursor from the real connection"""
        if self._closed:
            raise psycopg2.OperationalError("Connection is closed")
        return self._real_conn.cursor(*args, **kwargs)
    
    def commit(self):
        """Commit transaction"""
        if self._closed:
            raise psycopg2.OperationalError("Connection is closed")
        return self._real_conn.commit()
    
    def rollback(self):
        """Rollback transaction"""
        if self._closed:
            raise psycopg2.OperationalError("Connection is closed")
        return self._real_conn.rollback()
