from pydantic import BaseModel
from typing import Any, Optional

class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[any]=None
    
class ErrorResponse(BaseResponse):
    success: bool = False
    data: None = None
    