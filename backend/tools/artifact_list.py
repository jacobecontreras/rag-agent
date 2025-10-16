import logging
from typing import Dict, Any
from database.database import get_db_cursor

logger = logging.getLogger(__name__)


def artifact_list(input_data: Dict[str, Any]) -> Dict[str, Any]:
    job_name = input_data.get("job_name")

    logger.info(f"Fetching artifact list for job_name: '{job_name}'")

    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT DISTINCT at.id, at.file_name, COUNT(ad.row_index) as row_count
            FROM artifact_types at
            LEFT JOIN artifact_data ad ON at.id = ad.artifact_type_id AND ad.job_name = ?
            GROUP BY at.id, at.file_name
            ORDER BY at.file_name
            """

            cursor.execute(query, (job_name,))
            rows = cursor.fetchall()

            artifacts = []
            for row in rows:
                artifacts.append({
                    "id": row[0],
                    "file_name": row[1],
                    "row_count": row[2]
                })

            logger.info(f"Successfully retrieved {len(artifacts)} artifacts for job '{job_name}'")
            return {
                "success": True,
                "artifacts": artifacts,
                "count": len(artifacts)
            }
    except Exception as e:
        logger.error(f"Failed to fetch artifact list for job '{job_name}': {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }