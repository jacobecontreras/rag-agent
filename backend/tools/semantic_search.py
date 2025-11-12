import logging
from typing import Dict, Any
from services.chroma_service import chroma_service

from .shared_utils import build_error_response

logger = logging.getLogger(__name__)


def semantic_search(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform semantic search."""
    query = input_data["query"]
    job_name = input_data.get("job_name")  # Optional
    n_results = input_data["n_results"]

    try:
        results = chroma_service.query_chunks(query, job_name, n_results)
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Semantic search failed: {str(e)}")
        return build_error_response("semantic_search_error", str(e))