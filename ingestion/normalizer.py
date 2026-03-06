from datetime import datetime
from typing import Optional
from pydantic import BaseModel

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
        "ph": "pH",
        "level": "%",
        "pressure": "Pa",
        "pm25": "µg/m³",
        "voc": "ppb"
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
    
    # 3. Determiniamo il tipo di metrica dall'ID (l'ultima parola dopo l'underscore)
    # Esempio: "greenhouse_temperature" -> "temperature"
    metric_type = sensor_id.split('_')[-1]

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