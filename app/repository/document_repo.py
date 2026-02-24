from app.database import get_db
from typing import Optional


def insert_document(project_id: Optional[int], client_po_id: Optional[int], original_filename: str, stored_filename: str,
                    compressed_filename: str, mime_type: str, original_size: int,
                    compressed_size: int, description: str = None, uploaded_by: int = None):
    conn = get_db()
    try:
        with conn:
            with conn.cursor() as cur:
                # Try inserting including client_po_id. If the DB schema hasn't been migrated
                # and the column doesn't exist, fall back to inserting without client_po_id.
                try:
                    cur.execute("""
                        INSERT INTO project_document (
                            project_id, client_po_id, original_filename, stored_filename,
                            compressed_filename, mime_type, original_size,
                            compressed_size, description, uploaded_by
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        project_id, client_po_id, original_filename, stored_filename,
                        compressed_filename, mime_type, original_size,
                        compressed_size, description, uploaded_by
                    ))
                except Exception as e:
                    err = str(e).lower()
                    if 'client_po_id' in err or 'column "client_po_id"' in err:
                        # Retry without client_po_id column
                        cur.execute("""
                            INSERT INTO project_document (
                                project_id, original_filename, stored_filename,
                                compressed_filename, mime_type, original_size,
                                compressed_size, description, uploaded_by
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            project_id, original_filename, stored_filename,
                            compressed_filename, mime_type, original_size,
                            compressed_size, description, uploaded_by
                        ))
                    else:
                        # Unknown error, re-raise
                        raise

                return cur.fetchone()["id"]
    finally:
        conn.close()


def get_documents_for_project(project_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                  SELECT id, project_id, client_po_id, original_filename, stored_filename,
                      compressed_filename, mime_type, original_size,
                      compressed_size, description, uploaded_by, created_at
                FROM project_document
                WHERE project_id = %s
                ORDER BY created_at DESC
            """, (project_id,))

            rows = cur.fetchall()
            return [
                {
                    "id": r["id"],
                    "project_id": r["project_id"],
                    "client_po_id": r.get("client_po_id"),
                    "original_filename": r["original_filename"],
                    "stored_filename": r["stored_filename"],
                    "compressed_filename": r["compressed_filename"],
                    "mime_type": r["mime_type"],
                    "original_size": r["original_size"],
                    "compressed_size": r["compressed_size"],
                    "description": r["description"],
                    "uploaded_by": r["uploaded_by"],
                    "created_at": r["created_at"].isoformat() if r["created_at"] else None
                }
                for r in rows
            ]
    finally:
        conn.close()


def get_document_by_id(doc_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                  SELECT id, project_id, client_po_id, original_filename, stored_filename,
                      compressed_filename, mime_type, original_size,
                      compressed_size, description, uploaded_by, created_at
                FROM project_document
                WHERE id = %s
            """, (doc_id,))

            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "project_id": row["project_id"],
                "client_po_id": row.get("client_po_id"),
                "original_filename": row["original_filename"],
                "stored_filename": row["stored_filename"],
                "compressed_filename": row["compressed_filename"],
                "mime_type": row["mime_type"],
                "original_size": row["original_size"],
                "compressed_size": row["compressed_size"],
                "description": row["description"],
                "uploaded_by": row["uploaded_by"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None
            }
    finally:
        conn.close()


def get_documents_for_po(client_po_id: int):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, project_id, client_po_id, original_filename, stored_filename,
                       compressed_filename, mime_type, original_size,
                       compressed_size, description, uploaded_by, created_at
                FROM project_document
                WHERE client_po_id = %s
                ORDER BY created_at DESC
            """, (client_po_id,))

            rows = cur.fetchall()
            return [
                {
                    "id": r["id"],
                    "project_id": r["project_id"],
                    "client_po_id": r.get("client_po_id"),
                    "original_filename": r["original_filename"],
                    "stored_filename": r["stored_filename"],
                    "compressed_filename": r["compressed_filename"],
                    "mime_type": r["mime_type"],
                    "original_size": r["original_size"],
                    "compressed_size": r["compressed_size"],
                    "description": r["description"],
                    "uploaded_by": r["uploaded_by"],
                    "created_at": r["created_at"].isoformat() if r["created_at"] else None
                }
                for r in rows
            ]
    finally:
        conn.close()
