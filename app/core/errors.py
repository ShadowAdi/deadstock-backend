from datetime import datetime
from typing import Optional, Dict, Any

class AppError(Exception):
    """Custom application error with detailed context"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "APP_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for API responses"""
        return {
            "success": False,
            "error": self.message,
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "details": self.details
        }