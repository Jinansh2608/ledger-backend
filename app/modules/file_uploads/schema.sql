"""
Database schema for file upload sessions and files
"""

SQL_CREATE_UPLOAD_SESSION_TABLE = """
CREATE TABLE IF NOT EXISTS upload_session (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active',  -- active, expired, closed
    INDEX idx_expires_at (expires_at),
    INDEX idx_status (status)
);
"""

SQL_CREATE_UPLOAD_FILE_TABLE = """
CREATE TABLE IF NOT EXISTS upload_file (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
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
    status VARCHAR(20) DEFAULT 'active',  -- active, deleted, quarantined
    
    FOREIGN KEY (session_id) REFERENCES upload_session(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id),
    INDEX idx_po_number (po_number),
    INDEX idx_upload_timestamp (upload_timestamp),
    INDEX idx_status (status)
);
"""

SQL_CREATE_UPLOAD_STATS_TABLE = """
CREATE TABLE IF NOT EXISTS upload_stats (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    total_uploads INT DEFAULT 0,
    total_downloads INT DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES upload_session(session_id) ON DELETE CASCADE,
    INDEX idx_session_id (session_id)
);
"""

# Combined migration
MIGRATION_FILE_UPLOADS = f"""
SET search_path TO "Finances";

{SQL_CREATE_UPLOAD_SESSION_TABLE}

{SQL_CREATE_UPLOAD_FILE_TABLE}

{SQL_CREATE_UPLOAD_STATS_TABLE}

-- Create trigger to update upload_stats on new file
CREATE OR REPLACE FUNCTION update_upload_stats() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO upload_stats (id, session_id, total_uploads, total_size_bytes)
    VALUES (gen_random_uuid()::text, NEW.session_id, 1, NEW.file_size)
    ON CONFLICT (session_id) DO UPDATE SET
        total_uploads = total_uploads + 1,
        total_size_bytes = total_size_bytes + NEW.file_size,
        last_activity = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_upload_stats ON upload_file;
CREATE TRIGGER trigger_update_upload_stats
AFTER INSERT ON upload_file
FOR EACH ROW
EXECUTE FUNCTION update_upload_stats();
"""
