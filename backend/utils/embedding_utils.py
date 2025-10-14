import logging
from typing import List, Dict, Any
from services.chroma_service import chroma_service
from database.database import get_db_cursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_artifact_chunks(job_name: str) -> List[Dict[str, Any]]:
    """Retrieve all artifact data rows for a specific job"""
    try:
        with get_db_cursor() as cursor:
            query = """
            SELECT
                ad.job_name,
                ad.artifact_type_id,
                ad.row_index,
                ad.data_json,
                at.file_name
            FROM artifact_data ad
            JOIN artifact_types at ON ad.artifact_type_id = at.id
            WHERE ad.job_name = ?
            ORDER BY ad.artifact_type_id, ad.row_index
            """
            cursor.execute(query, (job_name,))
            rows = cursor.fetchall()

            return [
                {
                    'job_name': row[0],
                    'artifact_type_id': row[1],
                    'row_index': row[2],
                    'data_json': row[3],
                    'file_name': row[4]
                }
                for row in rows
            ]

    except Exception as e:
        logger.error(f"Error retrieving artifact data for {job_name}: {e}")
        return []


def embed_job_data(job_name: str) -> bool:
    """Embed all artifact data for a job"""
    chunks = get_artifact_chunks(job_name)

    if not chunks:
        logger.info(f"No artifact data found for job: {job_name}")
        return False

    try:
        success = chroma_service.embed_and_store_chunks(job_name, chunks)
        if success:
            logger.info(f"Successfully embedded data for job: {job_name}")
        else:
            logger.error(f"Failed to embed data for job: {job_name}")
        return success

    except Exception as e:
        logger.error(f"Error embedding data for job {job_name}: {e}")
        return False