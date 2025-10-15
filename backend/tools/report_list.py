from typing import Dict, Any
from database.database import get_db_cursor


def report_list(input_data: Dict[str, Any]) -> Dict[str, Any]:
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

            return {
                "success": True,
                "reports": reports,
                "count": len(reports)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }