import logging
from typing import Dict, Any, List, Optional, Tuple
from database.database import get_db_cursor

logger = logging.getLogger(__name__)


def _build_error_response(error_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Generic error response builder."""
    return {
        "success": False,
        "error": f"{error_type}: {details.get('message', 'Unknown error')}",
        "error_type": error_type,
        **{k: v for k, v in details.items() if k != 'message'}
    }


def _validate_input_parameters(input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    job_name = input_data.get("job_name")
    artifact_type_id = input_data.get("artifact_type_id")
    limit = input_data.get("limit", 100)  # Default 100 results
    offset = input_data.get("offset", 0)  # Default 0 offset

    if not job_name:
        return _build_error_response("validation_error", {
            "message": "Job name is required"
        })

    if not artifact_type_id:
        return _build_error_response("validation_error", {
            "message": "Artifact type ID is required"
        })

    # Enforcement of 200 results per tool call
    if limit > 200:
        return _build_error_response("validation_error", {
            "message": "Number of results cannot surpass 200"
        })

    return {
        "job_name": job_name,
        "artifact_type_id": artifact_type_id,
        "limit": limit,
        "offset": offset
    }


def _validate_report_exists(cursor, job_name: str) -> Optional[Dict[str, Any]]:
    check_query = "SELECT job_name FROM reports WHERE job_name = ? LIMIT 1"
    cursor.execute(check_query, (job_name,))
    report_exists = cursor.fetchone()

    if not report_exists:
        logger.warning(f"Report '{job_name}' not found")
        return _build_error_response("report_not_found", {
            "message": f"Report '{job_name}' not found"
        })

    return None


def _get_available_artifacts(cursor, job_name: str) -> List[Dict[str, Any]]:
    available_artifacts_query = """
    SELECT DISTINCT at.id, at.file_name
    FROM artifact_types at
    JOIN artifact_data ad ON at.id = ad.artifact_type_id
    WHERE ad.job_name = ?
    ORDER BY at.file_name
    """
    cursor.execute(available_artifacts_query, (job_name,))
    all_available = cursor.fetchall()

    return [{"id": row[0], "name": row[1]} for row in all_available]


def _validate_artifact_types(cursor, job_name: str, artifact_type_id, available_artifacts: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
    # Get available artifacts once if not provided
    if available_artifacts is None:
        available_artifacts = _get_available_artifacts(cursor, job_name)

    # Convert to list of valid IDs for easy checking
    valid_ids = [artifact["id"] for artifact in available_artifacts]

    # Handle both single IDs and lists
    ids_to_check = artifact_type_id if isinstance(artifact_type_id, list) else [artifact_type_id]
    invalid_ids = [id for id in ids_to_check if id not in valid_ids]

    if invalid_ids:
        logger.warning(f"Invalid artifact type IDs {invalid_ids} for report '{job_name}'")
        return _build_error_response("artifact_not_found", {
            "message": f"Invalid artifact type IDs: {invalid_ids}",
            "invalid_ids": invalid_ids if len(invalid_ids) > 1 else invalid_ids[0],
            "available_artifacts": available_artifacts
        })

    return None


def _build_artifact_query(job_name: str, artifact_type_id, limit: int, offset: int) -> Tuple[str, tuple]:
    if isinstance(artifact_type_id, list):
        # Create placeholders for IN clause: ?,?,? (one for each ID)
        placeholders = ','.join(['?'] * len(artifact_type_id))
        query = f"""
        SELECT ad.row_index, ad.data_json, at.file_name
        FROM artifact_data ad
        JOIN artifact_types at ON ad.artifact_type_id = at.id
        WHERE ad.job_name = ? AND ad.artifact_type_id IN ({placeholders})
        ORDER BY ad.artifact_type_id, ad.row_index
        LIMIT ? OFFSET ?
        """
        params = [job_name] + artifact_type_id + [limit, offset]
        logger.info(f"Querying multiple artifact types: {artifact_type_id}")
    else:
        # Single ID (backward compatibility)
        query = """
        SELECT ad.row_index, ad.data_json, at.file_name
        FROM artifact_data ad
        JOIN artifact_types at ON ad.artifact_type_id = at.id
        WHERE ad.job_name = ? AND ad.artifact_type_id = ?
        ORDER BY ad.row_index
        LIMIT ? OFFSET ?
        """
        params = (job_name, artifact_type_id, limit, offset)
        logger.info(f"Querying single artifact type: {artifact_type_id}")

    return query, params


def _execute_artifact_query(cursor, query: str, params: tuple) -> List[Dict[str, Any]]:
    cursor.execute(query, params)
    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({
            "row_index": row[0],
            "data_json": row[1],
            "file_name": row[2]
        })

    return data


def _format_success_response(data: List[Dict[str, Any]], limit: int, offset: int) -> Dict[str, Any]:
    has_more = len(data) == limit

    return {
        "success": True,
        "data": data,
        "count": len(data),
        "limit": limit,
        "offset": offset,
        "has_more": has_more,
        "next_offset": offset + limit if has_more else None
    }


def artifact_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    # Validate input parameters
    params = _validate_input_parameters(input_data)
    if not params:
        return params  # This will be an error response

    job_name = params["job_name"]
    artifact_type_id = params["artifact_type_id"]
    limit = params["limit"]
    offset = params["offset"]

    logger.info(f"Fetching artifact data: job_name='{job_name}', artifact_type_id={artifact_type_id}, limit={limit}, offset={offset}")

    try:
        with get_db_cursor() as cursor:
            # Validate report exists
            error_response = _validate_report_exists(cursor, job_name)
            if error_response:
                return error_response

            # Get available artifacts once for caching
            available_artifacts = _get_available_artifacts(cursor, job_name)

            # Validate artifact type(s) exist for this report
            error_response = _validate_artifact_types(cursor, job_name, artifact_type_id, available_artifacts)
            if error_response:
                return error_response

            # Build and execute query
            query, params_tuple = _build_artifact_query(job_name, artifact_type_id, limit, offset)
            data = _execute_artifact_query(cursor, query, params_tuple)

            logger.info(f"Successfully retrieved {len(data)} artifact data rows for job '{job_name}'")

            # Format and return success response
            return _format_success_response(data, limit, offset)

    except Exception as e:
        logger.error(f"Failed to fetch artifact data for job '{job_name}', artifact_type_id={artifact_type_id}: {str(e)}")
        return _build_error_response("database_error", {
            "message": f"Database error: {str(e)}"
        })