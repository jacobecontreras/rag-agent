import logging
from .semantic_search import semantic_search
from .artifact_list import artifact_list
from .artifact_data import artifact_data
from .report_list import report_list

logger = logging.getLogger(__name__)

TOOLS = {
    "semanticSearch": semantic_search,
    "viewArtifactList": artifact_list,
    "viewArtifactData": artifact_data,
    "viewReportList": report_list
}

def execute_tool(name: str, input_data: dict):
    """Execute a tool by name with the given input data."""
    logger.info(f"Executing tool: '{name}' with input: {input_data}")

    tool = TOOLS.get(name)
    if tool:
        try:
            result = tool(input_data)
            if result.get("success"):
                logger.info(f"Tool '{name}' executed successfully")
            else:
                logger.warning(f"Tool '{name}' executed with error: {result.get('error')}")
            return result
        except Exception as e:
            logger.error(f"Unexpected error executing tool '{name}': {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    logger.error(f"Tool '{name}' not found")
    return {"success": False, "error": f"Tool '{name}' not found"}