from pydantic import BaseModel
from typing import Dict, Optional, List, Union
from datetime import datetime

class StandardFormat(BaseModel):
    id: str        # Esempio: greenhouse_temperature
    metric: str    # Esempio: temperature, ph, co2...
    timestamp: datetime
    value: Union[float, str]
    unit: Optional[str] = None
    origin: str    # La famiglia dello schema (es: rest.scalar.v1)
    status: Optional[str] = None
