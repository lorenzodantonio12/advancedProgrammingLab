from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import json
from datetime import datetime

# Definiamo lo schema che avete concordato nel team [cite: 72]
class StandardFormat(BaseModel):
    id: str        # Esempio: greenhouse_temperature
    metric: str    # Esempio: temperature, ph, co2...
    timestamp: datetime
    value: float
    unit: Optional[str] = None
    origin: str    # La famiglia dello schema (es: rest.scalar.v1)
    status: Optional[str] = None

def map_to_standard(sensor_id: str, raw_data: dict, schema_family: str) -> StandardFormat:
    """
    Prende i dati grezzi dal simulatore e li trasforma in StandardFormat.
    """
    
    # 1. Mappa delle unità di misura basata sui sensori REST 
    units = {
        "temperature": "°C",
        "humidity": "%",
        "co2": "ppm",
        "ph": "",
        "level": "%",
        "pressure": "hPa",
        "pm25": "µg/m³",
        "voc": "ppb",
        "radiation": "Sv/h",
        "power": "kW",
        "oxygen": "%",
        "cycles": "cycles/h"
    }

    # Mappa sensor_id a metric_type
    metric_map = {
        "greenhouse_temperature": "temperature",
        "entrance_humidity": "humidity",
        "co2_hall": "co2",
        "hydroponic_ph": "ph",
        "water_tank_level": "level",
        "corridor_pressure": "pressure",
        "air_quality_pm25": "pm25",
        "air_quality_voc": "voc",
        "radiation": "radiation",
        "solar_array": "power",
        "power_bus": "power",
        "power_consumption": "power",
        "life_support": "oxygen",
        "thermal_loop": "temperature",
        "airlock": "cycles"
    }

    # 2. Estraiamo il valore numerico dal JSON del simulatore.
    # I sensori REST mandano chiavi diverse (es: {"temp": 25} o {"ph": 7}). 
    # Questo trucco prende il primo valore numerico che trova nel dizionario.
    value = 0.0
    if isinstance(raw_data, dict):
        for v in raw_data.values():
            if isinstance(v, (int, float)):
                value = float(v)
                break
    
    # 3. Determiniamo il tipo di metrica dalla mappa
    metric_type = metric_map.get(sensor_id, sensor_id.split('_')[-1])

    # 4. Creiamo l'oggetto normalizzato
    return StandardFormat(
        id=sensor_id,
        metric=metric_type,
        timestamp=datetime.now(),
        value=value,
        unit=units.get(metric_type, "N/A"),
        origin=schema_family,
        status="OK"
    )

def to_json(data: StandardFormat) -> str:
    # Trasforma l'oggetto Pydantic in una stringa JSON
    # Usiamo isoformat per la data così il Member 2 non impazzisce a leggerla
    return data.model_dump_json()