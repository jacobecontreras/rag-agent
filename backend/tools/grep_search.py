import logging
import json
from typing import Dict, Any, List, Optional
from database.database import get_db_cursor

from .shared_utils import build_error_response

logger = logging.getLogger(__name__)


def grep_search(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Search for patterns in artifact data."""
    job_name = input_data["job_name"]
    pattern = input_data["pattern"].strip()
    artifact_type_id = input_data.get("artifact_type_id")
    limit = input_data["limit"]
    case_sensitive = input_data["case_sensitive"]

    if not pattern:
        return build_error_response("validation_error", "Search pattern cannot be empty")

    try:
        with get_db_cursor() as cursor:
            # Check if report exists
            cursor.execute("SELECT job_name FROM reports WHERE job_name = ? LIMIT 1", (job_name,))
            if not cursor.fetchone():
                return build_error_response("report_not_found", f"Report '{job_name}' not found")

            # Build search query
            conditions = ["ad.job_name = ?"]
            params = [job_name]

            if artifact_type_id is None:
                order_by = "ORDER BY at.file_name, ad.row_index"
            elif isinstance(artifact_type_id, list):
                placeholders = ','.join(['?'] * len(artifact_type_id))
                conditions.append(f"ad.artifact_type_id IN ({placeholders})")
                params.extend(artifact_type_id)
                order_by = "ORDER BY at.file_name, ad.row_index"
            else:
                conditions.append("ad.artifact_type_id = ?")
                params.append(artifact_type_id)
                order_by = "ORDER BY ad.row_index"

            # Add pattern filter
            if case_sensitive:
                conditions.append("ad.data_json LIKE ?")
                params.append(f"%{pattern}%")
            else:
                conditions.append("LOWER(ad.data_json) LIKE ?")
                params.append(f"%{pattern.lower()}%")

            params.append(limit)

            where_clause = " AND ".join(conditions)
            query = f"""
                SELECT ad.row_index, ad.data_json, at.file_name, at.id as artifact_type_id
                FROM artifact_data ad
                JOIN artifact_types at ON ad.artifact_type_id = at.id
                WHERE {where_clause}
                {order_by}
                LIMIT ?
            """

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            matches = []
            for row in rows:
                try:
                    data_json = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                    matches.append({
                        "row_index": row[0],
                        "data_json": data_json,
                        "file_name": row[2],
                        "artifact_type_id": row[3]
                    })
                except json.JSONDecodeError:
                    matches.append({
                        "row_index": row[0],
                        "data_json": row[1],
                        "file_name": row[2],
                        "artifact_type_id": row[3],
                        "parse_error": True
                    })

            return {
                "success": True,
                "matches": matches,
                "count": len(matches),
                "pattern": pattern,
                "job_name": job_name,
                "artifact_type_id": artifact_type_id
            }

    except Exception as e:
        logger.error(f"Grep search failed: {str(e)}")
        return build_error_response("database_error", f"Database error: {str(e)}")