import logging
from typing import Dict, Any
from database.database import get_db_cursor

logger = logging.getLogger(__name__)


def artifact_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    job_name = input_data.get("job_name")
    artifact_type_id = input_data.get("artifact_type_id")
    limit = input_data.get("limit", 100)

    logger.info(f"Fetching artifact data: job_name='{job_name}', artifact_type_id={artifact_type_id}, limit={limit}")

    try:
        with get_db_cursor() as cursor:
            # Handle both single ID and list of IDs
            if isinstance(artifact_type_id, list):
                # Create placeholders for IN clause: ?,?,? (one for each ID)
                placeholders = ','.join(['?'] * len(artifact_type_id))
                query = f"""
                SELECT ad.row_index, ad.data_json, at.file_name
                FROM artifact_data ad
                JOIN artifact_types at ON ad.artifact_type_id = at.id
                WHERE ad.job_name = ? AND ad.artifact_type_id IN ({placeholders})
                ORDER BY ad.artifact_type_id, ad.row_index
                LIMIT ?
                """
                params = [job_name] + artifact_type_id + [limit]
                logger.info(f"Querying multiple artifact types: {artifact_type_id}")
            else:
                # Single ID (backward compatibility)
                query = """
                SELECT ad.row_index, ad.data_json, at.file_name
                FROM artifact_data ad
                JOIN artifact_types at ON ad.artifact_type_id = at.id
                WHERE ad.job_name = ? AND ad.artifact_type_id = ?
                ORDER BY ad.row_index
                LIMIT ?
                """
                params = (job_name, artifact_type_id, limit)
                logger.info(f"Querying single artifact type: {artifact_type_id}")

            cursor.execute(query, params)
            rows = cursor.fetchall()

            data = []
            for row in rows:
                data.append({
                    "row_index": row[0],
                    "data_json": row[1],
                    "file_name": row[2]
                })

            logger.info(f"Successfully retrieved {len(data)} artifact data rows for job '{job_name}'")
            return {
                "success": True,
                "data": data,
                "count": len(data)
            }
    except Exception as e:
        logger.error(f"Failed to fetch artifact data for job '{job_name}', artifact_type_id={artifact_type_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }