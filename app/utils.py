from typing import Any, Dict, Optional

def create_response(success: bool, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Format response for Zoho SalesIQ API Plug.
    """
    response = {"success": success}
    if success:
        if data:
            response["data"] = data
        response.update(kwargs)
    else:
        response["error"] = error
    return response
