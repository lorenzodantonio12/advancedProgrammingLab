from pydantic import BaseModel
from typing import Dict, Optional, List, Union
from datetime import datetime

class StandardFormat(BaseModel):
    id: str        
    metric: str    
    timestamp: datetime
    value: float
    unit: Optional[str] = None
    origin: str    
    status: Optional[str] = None
