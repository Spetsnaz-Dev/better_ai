"""
Standardized API response helpers.
Use these to ensure consistent error/success response shapes across the app.
"""


def build_error_response(error_type, message, details=None):
    """Build a standardized error response dict.
    
    Args:
        error_type: Error category (e.g. 'ValidationError', 'NotFound')
        message: Human-readable error message
        details: Optional additional details (dict, list, or string)
    
    Returns:
        dict matching the API error contract:
        {"error": {"type": "...", "message": "...", "details": ...}}
    """
    response = {
        "error": {
            "type": error_type,
            "message": message,
        }
    }
    if details is not None:
        response["error"]["details"] = details
    return response


def build_success_response(data, message=None):
    """Build a standardized success response dict.
    
    Args:
        data: The response payload
        message: Optional success message
    
    Returns:
        dict with the data, optionally with a message
    """
    if message:
        return {"message": message, "data": data}
    return data
