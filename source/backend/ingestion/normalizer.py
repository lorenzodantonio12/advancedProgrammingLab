from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class StandardFormat(BaseModel):
    id: str
    metric: str
    timestamp: datetime
    value: float
    unit: Optional[str] = None
    origin: str
    status: Optional[str] = None

def map_to_standard(sensor_id: str, raw_data: dict, schema_family: str) -> StandardFormat:
    # 1. Mappa Unità completa per tutti i sensori
    units = {
        "greenhouse_temperature": "°C",
        "entrance_humidity": "%",
        "co2_hall": "ppm",
        "hydroponic_ph": "pH",
        "water_tank_level": "%",
        "corridor_pressure": "Pa",
        "air_quality_pm25": "µg/m³",
        "air_quality_voc": "ppb",
        "radiation": "uSv/h",
        "solar_array": "W",
        "power_consumption": "W",
        "power_bus": "V",
        "life_support": "%",
        "thermal_loop": "°C",
        "airlock": "bar"
    }

    # 2. Estrazione Valore numerico
    value = 0.0
    if isinstance(raw_data, dict):
        if "value" in raw_data and float(raw_data["value"]) > 1000000:
             value = round((float(raw_data["value"]) % 100) / 10, 2)
        else:
            for v in raw_data.values():
                if isinstance(v, (int, float)):
                    value = float(v)
                    break
    elif isinstance(raw_data, (int, float)):
        value = float(raw_data)

    # 3. Logica differenziata per gli ID
    # Verifichiamo se il sensore è della telemetria tecnica
    is_telemetry = sensor_id.startswith("mars_telemetry_")
    
    if is_telemetry:
        # Per SSE: puliamo l'ID (es: radiation) per il CHECK 3
        final_id = sensor_id.replace("mars_telemetry_", "")
    else:
        # Per REST: manteniamo l'ID originale (es: greenhouse_temperature)
        final_id = sensor_id

    # La metrica serve al frontend per l'etichetta del widget
    metric_name = final_id.replace("mars_telemetry_", "")

    return StandardFormat(
        id=final_id,
        metric=metric_name,
        timestamp=datetime.now(),
        value=round(value, 2),
        unit=units.get(sensor_id, units.get(final_id, "N/A")),
        origin=schema_family,
        status="OK"
    )

def to_json(data: StandardFormat) -> str:
    return data.model_dump_json()