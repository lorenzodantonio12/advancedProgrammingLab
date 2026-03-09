from datetime import datetime
from typing import Optional, Literal, Union
from pydantic import BaseModel

class StandardFormat(BaseModel):
    id: str        # Esempio: greenhouse_temperature
    metric: str    # Esempio: temperature, ph, co2...
    timestamp: datetime
    value: float
    unit: Optional[str] = None
    origin: str    # La famiglia dello schema (es: rest.scalar.v1)
    status: Optional[str] = None

class AutomationRule(BaseModel):
    id_rule: Optional[int] = None #not used if the frontend sends a request
    sensor_name: str
    operator: Literal["<", "<=", "=", ">", ">="]
    value: float
    metric: str
    actuator_name: str
    state: Literal["ON", "OFF"]