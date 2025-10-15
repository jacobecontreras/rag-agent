from typing import Dict, Any
from services.chroma_service import chroma_service


def semantic_search(input_data: Dict[str, Any]) -> Dict[str, Any]:
    query = input_data.get("query", "")
    job_name = input_data.get("job_name")
    n_results = input_data.get("n_results", 10)

    try:
        results = chroma_service.query_chunks(query, job_name, n_results)
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }