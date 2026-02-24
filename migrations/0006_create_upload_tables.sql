-- Migration: Create file upload tables
-- Description: Creates tables for file upload sessions, files, and statistics

SET search_path TO "Finances", public;

-- Create upload_session table
CREATE TABLE IF NOT EXISTS upload_session (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'active'
);

CREATE INDEX IF NOT EXISTS idx_upload_session_expires_at ON upload_session(expires_at);
CREATE INDEX IF NOT EXISTS idx_upload_session_status ON upload_session(status);
CREATE INDEX IF NOT EXISTS idx_upload_session_session_id ON upload_session(session_id);

-- Create upload_file table
CREATE TABLE IF NOT EXISTS upload_file (
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
    
    FOREIGN KEY (session_id) REFERENCES upload_session(session_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_upload_file_session_id ON upload_file(session_id);
CREATE INDEX IF NOT EXISTS idx_upload_file_po_number ON upload_file(po_number);
CREATE INDEX IF NOT EXISTS idx_upload_file_upload_timestamp ON upload_file(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_upload_file_status ON upload_file(status);

-- Create upload_stats table
CREATE TABLE IF NOT EXISTS upload_stats (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    total_uploads INT DEFAULT 0,
    total_downloads INT DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES upload_session(session_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_upload_stats_session_id ON upload_stats(session_id);

-- Create trigger to update upload_stats on new file
CREATE OR REPLACE FUNCTION update_upload_stats() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO upload_stats (id, session_id, total_uploads, total_size_bytes, last_activity)
    VALUES (gen_random_uuid()::text, NEW.session_id, 1, NEW.file_size, CURRENT_TIMESTAMP)
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
