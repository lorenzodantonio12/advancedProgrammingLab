from pydantic import BaseModel
from datetime import datetime
from typing import Any

class StandardFormat(BaseModel):
    id: str
    metric: str
    timestamp: datetime
    value: float
    unit: str
    origin: str
    status: str

def map_to_standard(sensor_id: str, raw_data: dict, schema_family: str) -> StandardFormat:
    value = 0.0
    
    # 1. Estrazione Valore (Gestione SSE e REST)
    if isinstance(raw_data, dict) and "measurements" in raw_data:
        try:
            value = float(raw_data["measurements"][0]["value"])
        except (IndexError, KeyError, TypeError, ValueError):
            value = 0.0
    elif isinstance(raw_data, dict):
        for v in raw_data.values():
            if isinstance(v, (int, float)):
                value = float(v)
                break
    
    # 2. Mappa Unità di Misura (Nomi completi per match perfetto)
    units_map = {
        "greenhouse_temperature": "°C",
        "entrance_humidity": "%",
        "hydroponic_ph": "pH",
        "water_tank_level": "%",
        "corridor_pressure": "Pa",
        "air_quality_pm25": "µg/m³",
        "air_quality_voc": "ppb",
        "co2_hall": "ppm",
        "mars_telemetry_radiation": "uSv/h",
        "mars_telemetry_solar_array": "W",
        "mars_telemetry_power_bus": "V",
        "mars_telemetry_power_consumption": "W",
        "mars_telemetry_thermal_loop": "°C",
        "mars_telemetry_airlock": "bar",
        "mars_telemetry_life_support": "%"
    }
    
    # Usiamo l'ID intero per trovare l'unità, così non sbagliamo più
    unit = units_map.get(sensor_id, "N/A")
    
    # Estraiamo un nome metrica leggibile (l'ultima parola dopo l'underscore)
    metric_name = sensor_id.split('_')[-1]

    return StandardFormat(
        id=sensor_id,
        metric=metric_name,
        timestamp=datetime.now(),
        value=value,
        unit=unit,
        origin=schema_family,
        status="OK"
    )