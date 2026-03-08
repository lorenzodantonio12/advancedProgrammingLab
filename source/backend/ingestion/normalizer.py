from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class StandardFormat(BaseModel):
    id: str
    metric: str
    timestamp: datetime
    value: float
    unit: str
    origin: str
    status: str

def map_to_standard(sensor_id: str, raw_data: Any, schema_family: str) -> StandardFormat:
    """
    Normalizzatore basato sui contratti v1.2.0 del Mars IoT Simulator.
    """
    value = 0.0
    unit = "N/A"
    
    # 1. LOGICA DI ESTRAZIONE VALORE BASATA SULLA STRUTTURA DEL JSON
    if not isinstance(raw_data, dict):
        return None # Errore nel dato grezzo

    # Caso A: rest.scalar.v1 (Greenhouse Temp, CO2, ecc.) o environment.v1 con metric/value
    if "value" in raw_data:
        value = float(raw_data["value"])
        unit = raw_data.get("unit", "N/A")

    # Caso B: rest.chemistry.v1 o topic.environment.v1 (Dati annidati in array)
    elif "measurements" in raw_data:
        # Prendiamo la prima misura disponibile nell'array
        m = raw_data["measurements"][0]
        value = float(m["value"])
        unit = m.get("unit", "N/A")

    # Caso C: rest.particulate.v1 (PM2.5)
    elif "pm25_ug_m3" in raw_data:
        value = float(raw_data["pm25_ug_m3"])
        unit = "µg/m³"

    # Caso D: rest.level.v1 (Water Tank)
    elif "level_pct" in raw_data:
        value = float(raw_data["level_pct"])
        unit = "%"

    # Caso E: topic.power.v1 (Solar Array, Power Consumption)
    elif "power_kw" in raw_data:
        value = float(raw_data["power_kw"])
        unit = "kW"

    # Caso F: topic.thermal_loop.v1
    elif "temperature_c" in raw_data:
        value = float(raw_data["temperature_c"])
        unit = "°C"

    # Caso G: topic.airlock.v1
    elif "cycles_per_hour" in raw_data:
        value = float(raw_data["cycles_per_hour"])
        unit = "cycles/h"

    # 2. GESTIONE ID PER IL FRONTEND
    # Puliamo l'ID solo se è Telemetria SSE (inizia con mars/telemetry/)
    # I sensori REST rimangono col nome del contratto (es: greenhouse_temperature)
    is_telemetry = sensor_id.startswith("mars/telemetry/") or sensor_id.startswith("mars_telemetry_")
    
    if is_telemetry:
        # Trasforma 'mars/telemetry/radiation' -> 'radiation'
        final_id = sensor_id.split('/')[-1].replace("mars_telemetry_", "")
    else:
        final_id = sensor_id

    # La metrica è il nome dell'ID normalizzato
    metric_name = final_id

    return StandardFormat(
        id=final_id,
        metric=metric_name,
        timestamp=datetime.now(),
        value=round(value, 2),
        unit=unit,
        origin=schema_family,
        status=raw_data.get("status", "ok").upper()
    )

def to_json(data: StandardFormat) -> str:
    return data.model_dump_json()