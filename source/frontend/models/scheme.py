from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

class StandardFormat(BaseModel):
    id: str #esempio: greenhouse_temperature
    metric: str #esempio: temperature, ph, ...
    timestamp: datetime
    value: float
    unit: Optional[str] = None #unità di misura se serve
    origin: str #famiglia dello schema
    status: Optional[str] = None #ok, ...
