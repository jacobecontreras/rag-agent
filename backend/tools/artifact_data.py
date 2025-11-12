import logging
from typing import Dict, Any, List, Union
from database.database import get_db_cursor

from .shared_utils import build_error_response

logger = logging.getLogger(__name__)


def artifact_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get artifact data for a report."""
    job_name = input_data["job_name"]
    artifact_type_id = input_data["artifact_type_id"]
    limit = input_data["limit"]
    offset = input_data["offset"]

    try:
        with get_db_cursor() as cursor:
            # Check if report exists
            cursor.execute("SELECT job_name FROM reports WHERE job_name = ? LIMIT 1", (job_name,))
            if not cursor.fetchone():
                return build_error_response("report_not_found", f"Report '{job_name}' not found")

            # Validate artifact types
            cursor.execute("""
                SELECT DISTINCT at.id, at.file_name
                FROM artifact_types at
                JOIN artifact_data ad ON at.id = ad.artifact_type_id
                WHERE ad.job_name = ?
                ORDER BY at.file_name
            """, (job_name,))
            available_artifacts = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]

            valid_ids = [artifact["id"] for artifact in available_artifacts]
            ids_to_check = artifact_type_id if isinstance(artifact_type_id, list) else [artifact_type_id]
            invalid_ids = [id for id in ids_to_check if id not in valid_ids]

            if invalid_ids:
                return build_error_response(
                    "artifact_not_found",
                    f"Invalid artifact type IDs: {invalid_ids}",
                    invalid_ids=invalid_ids if len(invalid_ids) > 1 else invalid_ids[0],
                    available_artifacts=available_artifacts
                )

            # Build and execute query
            if isinstance(artifact_type_id, list):
                placeholders = ','.join(['?'] * len(artifact_type_id))
                query = f"""
                    SELECT ad.row_index, ad.data_json, at.file_name
                    FROM artifact_data ad
                    JOIN artifact_types at ON ad.artifact_type_id = at.id
                    WHERE ad.job_name = ? AND ad.artifact_type_id IN ({placeholders})
                    ORDER BY ad.artifact_type_id, ad.row_index
                    LIMIT ? OFFSET ?
                """
                params = [job_name] + artifact_type_id + [limit, offset]
            else:
                query = """
                    SELECT ad.row_index, ad.data_json, at.file_name
                    FROM artifact_data ad
                    JOIN artifact_types at ON ad.artifact_type_id = at.id
                    WHERE ad.job_name = ? AND ad.artifact_type_id = ?
                    ORDER BY ad.row_index
                    LIMIT ? OFFSET ?
                """
                params = (job_name, artifact_type_id, limit, offset)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            data = []
            for row in rows:
                data.append({
                    "row_index": row[0],
                    "data_json": row[1],
                    "file_name": row[2]
                })

            return {
                "success": True,
                "data": data,
                "count": len(data),
                "limit": limit,
                "offset": offset,
                "has_more": len(data) == limit,
                "next_offset": offset + limit if len(data) == limit else None
            }

    except Exception as e:
        logger.error(f"Failed to fetch artifact data: {str(e)}")
        return build_error_response("database_error", f"Database error: {str(e)}")