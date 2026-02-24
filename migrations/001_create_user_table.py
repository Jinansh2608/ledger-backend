"""
Database migration to create user table for authentication
Run this before using the auth endpoints
"""
import psycopg2
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

def create_user_table():
    """Create the user table if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        
        with conn.cursor() as cur:
            # Create schema if not exists
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{settings.DB_SCHEMA}"')
            
            # Set search path to schema
            cur.execute(f'SET search_path TO "{settings.DB_SCHEMA}"')
            
            # Create user table
            cur.execute(f'''
                CREATE TABLE IF NOT EXISTS "user" (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cur.execute(f'CREATE INDEX IF NOT EXISTS idx_user_username ON "user" (username)')
            cur.execute(f'CREATE INDEX IF NOT EXISTS idx_user_email ON "user" (email)')
            
            conn.commit()
            logger.info("User table created successfully")
            
    except Exception as e:
        logger.error(f"Error creating user table: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Creating user table for authentication...")
    create_user_table()
    print("User table created successfully!")
