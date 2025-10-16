import logging
from typing import Dict, Any
from database.database import get_db_cursor

logger = logging.getLogger(__name__)


def report_list(input_data: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Fetching report list")

    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT id, job_name, upload_date, status, error_message
            FROM reports
            ORDER BY upload_date DESC
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            reports = []
            for row in rows:
                reports.append({
                    "id": row[0],
                    "job_name": row[1],
                    "upload_date": row[2],
                    "status": row[3],
                    "error_message": row[4]
                })

            logger.info(f"Successfully retrieved {len(reports)} reports")
            return {
                "success": True,
                "reports": reports,
                "count": len(reports)
            }
    except Exception as e:
        logger.error(f"Failed to fetch report list: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }