import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from database.database import get_db_cursor

# Import shared validation helpers from artifact_data.py
from .artifact_data import _validate_report_exists, _validate_artifact_types, _get_available_artifacts

logger = logging.getLogger(__name__)


def _build_error_response(error_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Generic error response builder."""
    return {
        "success": False,
        "error": f"{error_type}: {details.get('message', 'Unknown error')}",
        "error_type": error_type,
        **{k: v for k, v in details.items() if k != 'message'}
    }


def _validate_search_params(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate search input parameters."""
    pattern = input_data.get("pattern", "")
    job_name = input_data.get("job_name")
    artifact_type_id = input_data.get("artifact_type_id")
    limit = input_data.get("limit", 50)
    case_sensitive = input_data.get("case_sensitive", False)

    if not pattern:
        return _build_error_response("validation_error", {
            "message": "Pattern is required for search"
        })

    if not job_name:
        return _build_error_response("validation_error", {
            "message": "Job name is required"
        })

    if limit > 200:
        return _build_error_response("validation_error", {
            "message": "Number of results cannot surpass 200"
        })

    return {
        "success": True,
        "pattern": pattern,
        "job_name": job_name,
        "artifact_type_id": artifact_type_id,
        "limit": limit,
        "case_sensitive": case_sensitive
    }


def _build_search_query(job_name: str, artifact_type_id: Optional[Any],
                       pattern: str, case_sensitive: bool, limit: int) -> Tuple[str, tuple]:
    """Build dynamic search query based on parameters."""

    # Build WHERE clause conditions
    conditions = ["ad.job_name = ?"]
    params = [job_name]

    # Add artifact type filter if specified
    if artifact_type_id is None:
        # Search all artifacts
        order_by = "ORDER BY at.file_name, ad.row_index"
    elif isinstance(artifact_type_id, list):
        # Search specific multiple artifact types
        placeholders = ','.join(['?'] * len(artifact_type_id))
        conditions.append(f"ad.artifact_type_id IN ({placeholders})")
        params.extend(artifact_type_id)
        order_by = "ORDER BY at.file_name, ad.row_index"
    else:
        # Search single artifact type
        conditions.append("ad.artifact_type_id = ?")
        params.append(artifact_type_id)
        order_by = "ORDER BY ad.row_index"

    # Add pattern filter
    if case_sensitive:
        conditions.append("ad.data_json LIKE ?")
        params.append(f"%{pattern}%")
    else:
        conditions.append("LOWER(ad.data_json) LIKE ?")
        params.append(f"%{pattern.lower()}%")

    # Add limit
    params.append(limit)

    # Build final query
    where_clause = " AND ".join(conditions)
    query = f"""
    SELECT ad.row_index, ad.data_json, at.file_name, at.id as artifact_type_id
    FROM artifact_data ad
    JOIN artifact_types at ON ad.artifact_type_id = at.id
    WHERE {where_clause}
    {order_by}
    LIMIT ?
    """

    return query, tuple(params)


def _execute_search(cursor, query: str, params: tuple) -> List[Dict[str, Any]]:
    """Execute search query and parse JSON results."""
    cursor.execute(query, params)
    rows = cursor.fetchall()

    matches = []
    for row in rows:
        try:
            data_json = json.loads(row[1]) if isinstance(row[1], str) else row[1]
            matches.append({
                "row_index": row[0],
                "data_json": data_json,
                "file_name": row[2],
                "artifact_type_id": row[3]
            })
        except json.JSONDecodeError:
            # If JSON parsing fails, include raw content with error flag
            matches.append({
                "row_index": row[0],
                "data_json": row[1],
                "file_name": row[2],
                "artifact_type_id": row[3],
                "parse_error": True
            })

    return matches


def grep_search(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Perform pattern search across artifact data using text matching."""
    # Validate input parameters
    validation_result = _validate_search_params(input_data)
    if not validation_result["success"]:
        return validation_result

    job_name = validation_result["job_name"]
    pattern = validation_result["pattern"]
    artifact_type_id = validation_result["artifact_type_id"]
    limit = validation_result["limit"]
    case_sensitive = validation_result["case_sensitive"]

    logger.info(f"Performing grep search: pattern='{pattern}', job_name='{job_name}', artifact_type_id={artifact_type_id}, limit={limit}")

    try:
        with get_db_cursor() as cursor:
            # Validate report exists
            validation_result = _validate_report_exists(cursor, job_name)
            if validation_result is not None:
                return validation_result

            # Validate artifact types (if specified)
            if artifact_type_id is not None:
                available_artifacts = _get_available_artifacts(cursor, job_name)
                validation_result = _validate_artifact_types(cursor, job_name, artifact_type_id, available_artifacts)
                if validation_result is not None:
                    return validation_result

            # Build and execute search query
            query, params = _build_search_query(job_name, artifact_type_id, pattern, case_sensitive, limit)
            matches = _execute_search(cursor, query, params)

            logger.info(f"Grep search completed successfully, found {len(matches)} matches")
            return {
                "success": True,
                "matches": matches,
                "count": len(matches),
                "pattern": pattern,
                "job_name": job_name,
                "artifact_type_id": artifact_type_id
            }

    except Exception as e:
        logger.error(f"Grep search failed: {str(e)}")
        return _build_error_response("database_error", {
            "message": f"Database error: {str(e)}"
        })