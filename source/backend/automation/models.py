from datetime import datetime
from typing import Optional, Literal, Union
from pydantic import BaseModel

class StandardFormat(BaseModel):
    id: str       
    metric: str  
    timestamp: datetime
    value: Union[float, str]
    unit: Optional[str] = None
    origin: str 
    status: Optional[str] = None

class AutomationRule(BaseModel):
    id_rule: Optional[int] = None 
    sensor_name: str
    operator: Literal["<", "<=", "=", ">", ">="]
    value: Union[float, str]
    metric: str
    actuator_name: str
    state: Literal["ON", "OFF"]