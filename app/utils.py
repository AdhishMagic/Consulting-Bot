from typing import Any, Dict, Optional

def create_response(success: bool, data: Optional[Dict[str, Any]] = None, message: Optional[str] = None, error: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format response for Zoho SalesIQ API Plug.
    Structure:
    {
       "success": true/false,
       "data": { ... },       # Payload
       "message": "...",      # Optional success message
       "error": "...",        # Error message if success is false
       "details": { ... }     # Error details
    }
    """
    response = {"success": success}
    
    if success:
        response["data"] = data if data is not None else {}
        if message:
            response["message"] = message
    else:
        response["error"] = error if error else "Unknown error"
        if details:
            response["details"] = details
            
    return response
