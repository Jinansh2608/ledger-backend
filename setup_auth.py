#!/usr/bin/env python
"""
Setup authentication system
Run this script once to create the user table in the database
"""
import sys
import os
import psycopg2

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            print("User table created successfully")
            
    except Exception as e:
        logger.error(f"Error creating user table: {e}")
        print(f"Error creating user table: {e}")
        raise
    finally:
        if conn:
            conn.close()

def main():
    print("=" * 60)
    print("Setting up Authentication System")
    print("=" * 60)
    
    try:
        print("\n1. Creating user table...")
        create_user_table()
        print("   ✓ User table created successfully!")
        
        print("\n" + "=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print("\nYou can now use the following authentication endpoints:")
        print("  • POST /api/auth/signup  - Register a new user")
        print("  • POST /api/auth/login   - Login with username/password")
        print("  • GET  /api/auth/me      - Get current user info (requires token)")
        print("\nSee docs/AUTH_API.md for usage examples")
        
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
