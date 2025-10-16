import logging
from typing import Dict, Any
from services.chroma_service import chroma_service

logger = logging.getLogger(__name__)


def semantic_search(input_data: Dict[str, Any]) -> Dict[str, Any]:
    query = input_data.get("query", "")
    job_name = input_data.get("job_name")
    n_results = input_data.get("n_results", 10)

    logger.info(f"Performing semantic search: query='{query}', job_name='{job_name}', n_results={n_results}")

    try:
        results = chroma_service.query_chunks(query, job_name, n_results)
        logger.info(f"Semantic search completed successfully, found {len(results)} results")
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Semantic search failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }