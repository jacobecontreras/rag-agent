import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Simplified constants for desktop app
DEFAULT_LIMIT = 100
DEFAULT_SEARCH_LIMIT = 50
DEFAULT_SEMANTIC_RESULTS = 10


def build_error_response(error_type: str, message: str, **extra_fields) -> Dict[str, Any]:
    """Simple error response builder for desktop application."""
    response = {
        "success": False,
        "error": f"{error_type}: {message}",
        "error_type": error_type,
        **extra_fields
    }
    logger.error(response['error'])
    return response