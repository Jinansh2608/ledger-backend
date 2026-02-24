"""
Repository layer for file upload database operations
"""

from app.database import get_db
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import json
from psycopg2.extras import Json

class UploadSessionRepository:
    """Repository for upload session database operations"""
    
    @staticmethod
    def create_session(
        session_id: str,
        expires_at: datetime,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new upload session"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO upload_session (id, session_id, expires_at, metadata, status)
                        VALUES (%s, %s, %s, %s, 'active')
                        RETURNING id, session_id, created_at, expires_at, metadata, status
                    """, (str(uuid.uuid4()), session_id, expires_at, Json(metadata or {})))
                    
                    return cur.fetchone()
        except Exception:
            conn.close()
            raise
        finally:
            try:
                conn.close()
            except:
                pass
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, session_id, created_at, expires_at, metadata, status
                        FROM upload_session
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    return cur.fetchone()
        finally:
            try:
                conn.close()
            except:
                pass
    
    @staticmethod
    def get_session_with_file_count(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session with file count and stats"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            us.id, us.session_id, us.created_at, us.expires_at, 
                            us.metadata, us.status,
                            COUNT(uf.id) as file_count,
                            COALESCE(SUM(uf.file_size), 0) as total_size
                        FROM upload_session us
                        LEFT JOIN upload_file uf ON us.session_id = uf.session_id AND uf.status = 'active'
                        WHERE us.session_id = %s
                        GROUP BY us.id, us.session_id, us.created_at, us.expires_at, us.metadata, us.status
                    """, (session_id,))
                    
                    return cur.fetchone()
        finally:
            try:
                conn.close()
            except:
                pass
    
    @staticmethod
    def is_session_expired(session_id: str) -> bool:
        """Check if session is expired"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Use SQL to compare timestamps to avoid timezone mismatches
                    cur.execute("""
                        SELECT expires_at < CURRENT_TIMESTAMP as is_expired
                        FROM upload_session
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    result = cur.fetchone()
                    if not result:
                        return True  # Session doesn't exist = expired
                    
                    return result['is_expired']
        finally:
            try:
                conn.close()
            except:
                pass
    
    @staticmethod
    def update_session_status(session_id: str, status: str) -> bool:
        """Update session status"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE upload_session
                        SET status = %s
                        WHERE session_id = %s
                    """, (status, session_id))
                    
                    return True
        finally:
            try:
                conn.close()
            except:
                pass
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete session and all related files"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM upload_session
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    return True
        finally:
            conn.close()


class UploadFileRepository:
    """Repository for file metadata database operations"""
    
    @staticmethod
    def create_file(
        session_id: str,
        po_number: Optional[str],
        original_filename: str,
        storage_filename: str,
        storage_path: str,
        file_size: int,
        mime_type: str,
        file_hash: Optional[str] = None,
        uploaded_by: Optional[str] = None,
        metadata: Dict[str, Any] = None,
        compressed_size: Optional[int] = None,
        is_compressed: bool = True,
        original_mime_type: Optional[str] = None,
        compressed_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save file metadata to database"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    file_id = str(uuid.uuid4())
                    cur.execute("""
                        INSERT INTO upload_file 
                        (id, session_id, po_number, original_filename, storage_filename, storage_path,
                         file_size, compressed_size, is_compressed, mime_type, original_mime_type, 
                         file_hash, compressed_hash, uploaded_by, metadata, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
                        RETURNING id, session_id, po_number, original_filename, storage_filename, storage_path,
                                  file_size, compressed_size, is_compressed, mime_type, original_mime_type,
                                  file_hash, compressed_hash, upload_timestamp, uploaded_by, status
                    """, (
                        file_id, session_id, po_number, original_filename, storage_filename, storage_path,
                        file_size, compressed_size or file_size, is_compressed, mime_type, 
                        original_mime_type or mime_type, file_hash, compressed_hash or file_hash, 
                        uploaded_by, Json(metadata or {})
                    ))
                    
                    return cur.fetchone()
        finally:
            conn.close()
    
    @staticmethod
    def get_file(file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by ID"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, session_id, original_filename, storage_filename, storage_path,
                               file_size, mime_type, file_hash, upload_timestamp, uploaded_by, status
                        FROM upload_file
                        WHERE id = %s AND status = 'active'
                    """, (file_id,))
                    
                    return cur.fetchone()
        finally:
            conn.close()
    
    @staticmethod
    def get_file_if_belongs_to_session(file_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get file and verify it belongs to the session"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, session_id, original_filename, storage_filename, storage_path,
                               file_size, mime_type, file_hash, upload_timestamp, uploaded_by, status
                        FROM upload_file
                        WHERE id = %s AND session_id = %s AND status = 'active'
                    """, (file_id, session_id))
                    
                    return cur.fetchone()
        finally:
            conn.close()
    
    @staticmethod
    def get_session_files(session_id: str, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Get all files for a session"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    if include_deleted:
                        cur.execute("""
                            SELECT id, session_id, original_filename, storage_filename, storage_path,
                                   file_size, mime_type, file_hash, upload_timestamp, uploaded_by, status
                            FROM upload_file
                            WHERE session_id = %s
                            ORDER BY upload_timestamp DESC
                        """, (session_id,))
                    else:
                        cur.execute("""
                            SELECT id, session_id, original_filename, storage_filename, storage_path,
                                   file_size, mime_type, file_hash, upload_timestamp, uploaded_by, status
                            FROM upload_file
                            WHERE session_id = %s AND status = 'active'
                            ORDER BY upload_timestamp DESC
                        """, (session_id,))
                    
                    return cur.fetchall() or []
        finally:
            conn.close()
    
    @staticmethod
    def delete_file(file_id: str, soft_delete: bool = True) -> bool:
        """Delete file metadata (soft delete by default)"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    if soft_delete:
                        cur.execute("""
                            UPDATE upload_file
                            SET status = 'deleted'
                            WHERE id = %s
                        """, (file_id,))
                    else:
                        cur.execute("""
                            DELETE FROM upload_file
                            WHERE id = %s
                        """, (file_id,))
                    
                    return True
        finally:
            conn.close()
    
    @staticmethod
    def get_session_file_count(session_id: str) -> int:
        """Get count of active files in session"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*) as count FROM upload_file
                        WHERE session_id = %s AND status = 'active'
                    """, (session_id,))
                    
                    result = cur.fetchone()
                    return result['count'] if result else 0
        finally:
            conn.close()
    
    @staticmethod
    def get_files_by_po_number(po_number: str, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Get all files for a specific PO number"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    if include_deleted:
                        cur.execute("""
                            SELECT id, session_id, po_number, original_filename, storage_filename, storage_path,
                                   file_size, compressed_size, is_compressed, mime_type, original_mime_type,
                                   file_hash, compressed_hash, upload_timestamp, uploaded_by, status, metadata
                            FROM upload_file
                            WHERE po_number = %s
                            ORDER BY upload_timestamp DESC
                        """, (po_number,))
                    else:
                        cur.execute("""
                            SELECT id, session_id, po_number, original_filename, storage_filename, storage_path,
                                   file_size, compressed_size, is_compressed, mime_type, original_mime_type,
                                   file_hash, compressed_hash, upload_timestamp, uploaded_by, status, metadata
                            FROM upload_file
                            WHERE po_number = %s AND status = 'active'
                            ORDER BY upload_timestamp DESC
                        """, (po_number,))
                    
                    return cur.fetchall() or []
        finally:
            conn.close()
    
    @staticmethod
    def get_file_count_by_po(po_number: str) -> int:
        """Get count of active files for a PO number"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*) as count FROM upload_file
                        WHERE po_number = %s AND status = 'active'
                    """, (po_number,))
                    
                    result = cur.fetchone()
                    return result['count'] if result else 0
        finally:
            conn.close()
    
    @staticmethod
    def get_total_size_by_po(po_number: str) -> int:
        """Get total size of all files for a PO number"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COALESCE(SUM(file_size), 0) as total_size FROM upload_file
                        WHERE po_number = %s AND status = 'active'
                    """, (po_number,))
                    
                    result = cur.fetchone()
                    return result['total_size'] if result else 0
        finally:
            conn.close()
    
    @staticmethod
    def get_total_compressed_size_by_po(po_number: str) -> int:
        """Get total compressed size of all files for a PO number"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COALESCE(SUM(compressed_size), 0) as total_size FROM upload_file
                        WHERE po_number = %s AND status = 'active'
                    """, (po_number,))
                    
                    result = cur.fetchone()
                    return result['total_size'] if result else 0
        finally:
            conn.close()
    
    @staticmethod
    def get_session_total_size(session_id: str) -> int:
        """Get total size of all files in session"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COALESCE(SUM(file_size), 0) as total_size FROM upload_file
                        WHERE session_id = %s AND status = 'active'
                    """, (session_id,))
                    
                    result = cur.fetchone()
                    return result['total_size'] if result else 0
        finally:
            conn.close()


class UploadStatsRepository:
    """Repository for upload statistics"""
    
    @staticmethod
    def increment_download_count(session_id: str) -> bool:
        """Increment download count for a session"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Using actual column names from the database schema
                    cur.execute("""
                        UPDATE upload_stats
                        SET last_updated = CURRENT_TIMESTAMP
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    return True
        finally:
            conn.close()
    
    @staticmethod
    def get_stats(session_id: str) -> Optional[Dict[str, Any]]:
        """Get stats for a session"""
        conn = get_db()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Using actual column names from the database schema
                    cur.execute("""
                        SELECT total_files, total_sessions, total_size_bytes, last_updated
                        FROM upload_stats
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    result = cur.fetchone()
                    if result:
                        # Map to expected format for compatibility
                        return {
                            'total_uploads': result.get('total_files'),
                            'total_downloads': 0,  # Not tracked in new schema
                            'total_size_bytes': result.get('total_size_bytes'),
                            'last_activity': result.get('last_updated')
                        }
                    return result
        finally:
            conn.close()
