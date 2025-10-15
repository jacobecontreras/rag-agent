from .semantic_search import semantic_search
from .artifact_list import artifact_list
from .artifact_data import artifact_data
from .report_list import report_list

TOOLS = {
    "semanticSearch": semantic_search,
    "viewArtifactList": artifact_list,
    "viewArtifactData": artifact_data,
    "viewReportList": report_list
}

def execute_tool(name: str, input_data: dict):
    """Execute a tool by name with the given input data."""
    tool = TOOLS.get(name)
    if tool:
        return tool(input_data)
    return {"success": False, "error": f"Tool '{name}' not found"}