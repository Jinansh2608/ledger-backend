#!/usr/bin/env python3
"""Recreate upload tables with correct schema"""
from app.database import get_db

conn = get_db()
try:
    with conn:
        with conn.cursor() as cur:
            # Drop existing trigger
            print("Dropping trigger...")
            cur.execute("DROP TRIGGER IF EXISTS trigger_update_upload_stats ON \"Finances\".upload_file")
            
            # Drop old tables
            print("Dropping old tables...")
            cur.execute("DROP TABLE IF EXISTS \"Finances\".upload_stats CASCADE")
            cur.execute("DROP TABLE IF EXISTS \"Finances\".upload_file CASCADE")
            cur.execute("DROP TABLE IF EXISTS \"Finances\".upload_session CASCADE")
            
            # Recreate with correct schema
            print("Creating upload_session table...")
            cur.execute("""
                CREATE TABLE "Finances".upload_session (
                    id VARCHAR(36) PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    status VARCHAR(20) DEFAULT 'active',
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_session_expires_at ON \"Finances\".upload_session(expires_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_session_status ON \"Finances\".upload_session(status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_session_session_id ON \"Finances\".upload_session(session_id)")
            print("✓ upload_session created")
            
            print("Creating upload_file table...")
            cur.execute("""
                CREATE TABLE "Finances".upload_file (
                    id VARCHAR(36) PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    po_number VARCHAR(100),
                    original_filename VARCHAR(500) NOT NULL,
                    storage_filename VARCHAR(500) NOT NULL,
                    storage_path TEXT NOT NULL,
                    file_size BIGINT NOT NULL,
                    compressed_size BIGINT,
                    is_compressed BOOLEAN DEFAULT TRUE,
                    mime_type VARCHAR(100),
                    original_mime_type VARCHAR(100),
                    file_hash VARCHAR(64),
                    compressed_hash VARCHAR(64),
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_by VARCHAR(100),
                    metadata JSONB DEFAULT '{}',
                    status VARCHAR(20) DEFAULT 'active',
                    
                    FOREIGN KEY (session_id) REFERENCES "Finances".upload_session(session_id) ON DELETE CASCADE
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_file_session_id ON \"Finances\".upload_file(session_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_file_po_number ON \"Finances\".upload_file(po_number)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_file_upload_timestamp ON \"Finances\".upload_file(upload_timestamp)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_file_status ON \"Finances\".upload_file(status)")
            print("✓ upload_file created")
            
            print("Creating upload_stats table...")
            cur.execute("""
                CREATE TABLE "Finances".upload_stats (
                    id VARCHAR(36) PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL UNIQUE,
                    total_uploads INT DEFAULT 0,
                    total_downloads INT DEFAULT 0,
                    total_size_bytes BIGINT DEFAULT 0,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (session_id) REFERENCES "Finances".upload_session(session_id) ON DELETE CASCADE
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_upload_stats_session_id ON \"Finances\".upload_stats(session_id)")
            print("✓ upload_stats created")
            
            print("Creating trigger function...")
            cur.execute("""
                CREATE OR REPLACE FUNCTION "Finances".update_upload_stats() RETURNS TRIGGER AS $$
                BEGIN
                    INSERT INTO "Finances".upload_stats (id, session_id, total_uploads, total_size_bytes, last_activity)
                    VALUES (gen_random_uuid()::text, NEW.session_id, 1, NEW.file_size, CURRENT_TIMESTAMP)
                    ON CONFLICT (session_id) DO UPDATE SET
                        total_uploads = EXCLUDED.total_uploads + 1,
                        total_size_bytes = EXCLUDED.total_size_bytes + NEW.file_size,
                        last_activity = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            
            print("Creating trigger...")
            cur.execute("""
                CREATE TRIGGER trigger_update_upload_stats
                AFTER INSERT ON "Finances".upload_file
                FOR EACH ROW
                EXECUTE FUNCTION "Finances".update_upload_stats()
            """)
            print("✓ Trigger created")
            
            print("\n✅ All upload tables recreated successfully!")
finally:
    conn.close()
