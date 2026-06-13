import requests
import logging
from typing import Dict, Any
from apps.resume_analyzer.frontend.utils.constants import API_URL, ERR_API_UNAVAILABLE, ERR_MALFORMED_RESPONSE

logger = logging.getLogger(__name__)

class APIClient:
    """Core HTTP wrapper focusing on robust error handling."""
    
    @staticmethod
    def get(endpoint: str, timeout: int = 10) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{API_URL}{endpoint}", timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"API GET Error [{endpoint}]: {e}")
            return {"status": "error", "message": ERR_API_UNAVAILABLE}
        except ValueError as e:
            logger.error(f"API Decode Error [{endpoint}]: {e}")
            return {"status": "error", "message": ERR_MALFORMED_RESPONSE}

    @staticmethod
    def post(endpoint: str, payload: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        try:
            resp = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"API POST Error [{endpoint}]: {e}")
            return {"status": "error", "message": ERR_API_UNAVAILABLE}
        except ValueError as e:
            logger.error(f"API Decode Error [{endpoint}]: {e}")
            return {"status": "error", "message": ERR_MALFORMED_RESPONSE}

    @staticmethod
    def upload_files(endpoint: str, data: Dict[str, Any], files: list, timeout: int = 60) -> Dict[str, Any]:
        try:
            resp = requests.post(f"{API_URL}{endpoint}", data=data, files=files, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"API Upload Error [{endpoint}]: {e}")
            return {"status": "error", "message": ERR_API_UNAVAILABLE}
        except ValueError as e:
            logger.error(f"API Decode Error [{endpoint}]: {e}")
            return {"status": "error", "message": ERR_MALFORMED_RESPONSE}
