import logging
from typing import Dict, Any, List
from database.database import get_db_cursor

logger = logging.getLogger(__name__)


def _build_error_response(error_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "success": False,
        "error": f"{error_type}: {details.get('message', 'Unknown error')}",
        "error_type": error_type,
        **{k: v for k, v in details.items() if k != 'message'}
    }


def _validate_job_name(job_name: str) -> Dict[str, Any]:
    if not job_name:
        return _build_error_response("validation_error", {
            "message": "Job name is required"
        })
    return {"success": True, "job_name": job_name}


def _get_available_reports(cursor, limit: int = 10) -> List[str]:
    available_reports_query = "SELECT job_name, upload_date FROM reports ORDER BY upload_date DESC LIMIT ?"
    cursor.execute(available_reports_query, (limit,))
    available_reports = cursor.fetchall()
    return [row[0] for row in available_reports]


def _validate_report_exists(cursor, job_name: str) -> Dict[str, Any]:
    check_query = "SELECT job_name FROM reports WHERE job_name = ? LIMIT 1"
    cursor.execute(check_query, (job_name,))
    report_exists = cursor.fetchone()

    if not report_exists:
        available_reports = _get_available_reports(cursor)
        reports_list = ", ".join(f"'{name}'" for name in available_reports)

        logger.warning(f"Report '{job_name}' not found")
        return {
            "success": False,
            "error": f"report_not_found: Report '{job_name}' not found. Available reports: {reports_list}.",
            "error_type": "report_not_found",
            "available_reports": available_reports
        }

    return {"success": True}


def _fetch_artifacts(cursor, job_name: str) -> List[Dict[str, Any]]:
    query = """
    SELECT DISTINCT at.id, at.file_name, COUNT(ad.row_index) as row_count
    FROM artifact_types at
    LEFT JOIN artifact_data ad ON at.id = ad.artifact_type_id AND ad.job_name = ?
    GROUP BY at.id, at.file_name
    ORDER BY at.file_name
    """

    cursor.execute(query, (job_name,))
    rows = cursor.fetchall()

    return [{
        "id": row[0],
        "file_name": row[1],
        "row_count": row[2]
    } for row in rows]


def artifact_list(input_data: Dict[str, Any]) -> Dict[str, Any]:
    job_name = input_data.get("job_name")
    logger.info(f"Fetching artifact list for job_name: '{job_name}'")

    # Validate input parameters
    validation_result = _validate_job_name(job_name)
    if not validation_result["success"]:
        return validation_result

    try:
        with get_db_cursor() as cursor:
            # Validate report exists
            validation_result = _validate_report_exists(cursor, job_name)
            if not validation_result["success"]:
                return validation_result

            # Fetch artifacts for valid report
            artifacts = _fetch_artifacts(cursor, job_name)

            logger.info(f"Successfully retrieved {len(artifacts)} artifacts for job '{job_name}'")
            return {
                "success": True,
                "artifacts": artifacts,
                "count": len(artifacts)
            }

    except Exception as e:
        logger.error(f"Failed to fetch artifact list for job '{job_name}': {str(e)}")
        return _build_error_response("database_error", {
            "message": f"Database error: {str(e)}"
        })