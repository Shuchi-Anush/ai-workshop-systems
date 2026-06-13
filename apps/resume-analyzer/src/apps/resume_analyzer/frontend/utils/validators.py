from typing import Dict, Any

def validate_evaluation_response(response: Dict[str, Any]) -> bool:
    if not isinstance(response, dict):
        return False
    if response.get("status") == "error":
        return False
    if "candidates" not in response:
        return False
    return True
