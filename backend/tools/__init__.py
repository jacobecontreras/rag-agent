import logging
from typing import Dict, Any
from pydantic import ValidationError

from .shared_utils import build_error_response
from .semantic_search import semantic_search
from .artifact_list import artifact_list
from .artifact_data import artifact_data
from .report_list import report_list
from .grep_search import grep_search

logger = logging.getLogger(__name__)

# Direct tool mapping - simple for desktop app
TOOLS = {
    "semanticSearch": semantic_search,
    "viewArtifactList": artifact_list,
    "viewArtifactData": artifact_data,
    "viewReportList": report_list,
    "grepSearch": grep_search
}

# Simple schema mapping
from .validation_schemas import TOOL_SCHEMAS


def execute_tool(name: str, input_data: dict):
    """Execute tool with simple validation for desktop application."""
    logger.info(f"Executing tool: '{name}'")

    # Check if tool exists
    tool = TOOLS.get(name)
    if not tool:
        return build_error_response("tool_not_found", f"Tool '{name}' not found")

    # Get schema and validate
    schema = TOOL_SCHEMAS.get(name)
    if not schema:
        return build_error_response("validation_error", f"No validation schema found for tool '{name}'")

    try:
        # Validate input
        validated_data = schema(**input_data)
        # Execute tool
        result = tool(validated_data.model_dump())
        return result

    except ValidationError as e:
        error_details = [f"{'.'.join(str(loc) for loc in error['loc'])}: {error['msg']}" for error in e.errors()]
        return build_error_response(
            "validation_error",
            f"Validation failed: {'; '.join(error_details)}",
            validation_details=error_details
        )

    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return build_error_response("execution_error", str(e))