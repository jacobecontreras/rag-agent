from typing import Dict, Any
from database.database import get_db_cursor


def artifact_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    job_name = input_data.get("job_name")
    artifact_type_id = input_data.get("artifact_type_id")
    limit = input_data.get("limit", 100)

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
                "count": len(data)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }