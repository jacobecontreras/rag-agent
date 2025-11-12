import logging
from typing import Dict, Any, List
from database.database import get_db_cursor

from .shared_utils import build_error_response

logger = logging.getLogger(__name__)


def artifact_list(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get list of artifacts for a report."""
    job_name = input_data["job_name"]

    try:
        with get_db_cursor() as cursor:
            # Check if report exists and get available reports for error message
            cursor.execute("SELECT job_name FROM reports WHERE job_name = ? LIMIT 1", (job_name,))
            if not cursor.fetchone():
                cursor.execute("SELECT job_name FROM reports ORDER BY upload_date DESC LIMIT 10")
                available_reports = [row[0] for row in cursor.fetchall()]
                reports_list = ", ".join(f"'{name}'" for name in available_reports)
                return build_error_response(
                    "report_not_found",
                    f"Report '{job_name}' not found. Available reports: {reports_list}",
                    available_reports=available_reports
                )

            # Get artifacts for valid report
            query = """
                SELECT DISTINCT at.id, at.file_name, COUNT(ad.row_index) as row_count
                FROM artifact_types at
                LEFT JOIN artifact_data ad ON at.id = ad.artifact_type_id AND ad.job_name = ?
                GROUP BY at.id, at.file_name
                ORDER BY at.file_name
            """
            cursor.execute(query, (job_name,))
            rows = cursor.fetchall()

            artifacts = [{"id": row[0], "file_name": row[1], "row_count": row[2]} for row in rows]

            return {
                "success": True,
                "artifacts": artifacts,
                "count": len(artifacts)
            }

    except Exception as e:
        logger.error(f"Failed to fetch artifact list: {str(e)}")
        return build_error_response("database_error", f"Database error: {str(e)}")