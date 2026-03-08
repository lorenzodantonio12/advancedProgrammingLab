from typing import Dict
from models import StandardFormat

latest_sensor_state: Dict[str, StandardFormat] = {}
latest_actuator_state: Dict[str, str] = {}