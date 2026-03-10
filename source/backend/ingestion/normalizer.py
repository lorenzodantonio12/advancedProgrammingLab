from datetime import datetime
from typing import Optional, Any, List
from pydantic import BaseModel
from models import StandardFormat

def map_to_standard(sensor_id: str, raw_data: Any, schema_family: str) -> List[StandardFormat]:
    
    if not isinstance(raw_data, dict):
        return [] 
    
    # Puliamo l'ID solo se è Telemetria SSE (inizia con mars/telemetry/)
    is_telemetry = sensor_id.startswith("mars/telemetry/") or sensor_id.startswith("mars_telemetry_")
    if is_telemetry:
        # Trasforma 'mars/telemetry/radiation' -> 'radiation'
        final_id = sensor_id.split('/')[-1].replace("mars_telemetry_", "")
    else:
        final_id = sensor_id

    status_val = raw_data.get("status", "ok").upper()

    time_str = raw_data.get("captured_at") or raw_data.get("event_time")

    if time_str:
        try:
            # 2. Converte la stringa ISO (es. "2026-03-09T01:26:47Z") in un oggetto datetime
            timestamp_val = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError:
            timestamp_val = datetime.now()
    else:
        timestamp_val = datetime.now()

    results = []

    def add_metric(metric_name: str, value: Any, unit: str, possible_status: str = None):
        try:
            final_val = round(float(value), 2)
        except (ValueError, TypeError):
            final_val = str(value)

        final_status = possible_status if possible_status else status_val

        results.append(StandardFormat(
            id=final_id,
            metric=metric_name,
            timestamp=timestamp_val,
            value=final_val,
            unit=unit,
            origin=schema_family,
            status=final_status
        ))

    try:
        # --- Caso A: rest.scalar.v1 (Greenhouse Temp, CO2, ecc.) ---
        if schema_family == "rest.scalar.v1":
            add_metric(raw_data.get("metric", final_id), raw_data.get("value", 0.0), raw_data.get("unit", "N/A"))

        # --- Caso B: rest.chemistry.v1 o topic.environment.v1 (Array measurements) ---
        elif schema_family in ["rest.chemistry.v1", "topic.environment.v1"]:
            # pH idroponico, VOC, Radiazioni e Supporto vitale
            for m in raw_data.get("measurements", []):
                add_metric(m.get("metric", "unknown"), m.get("value", 0.0), m.get("unit", "N/A"))

        # --- Caso C: rest.particulate.v1 (PM2.5) ---
        elif schema_family == "rest.particulate.v1":
            if "pm1_ug_m3" in raw_data: add_metric("pm1", raw_data["pm1_ug_m3"], "µg/m³")
            if "pm25_ug_m3" in raw_data: add_metric("pm25", raw_data["pm25_ug_m3"], "µg/m³")
            if "pm10_ug_m3" in raw_data: add_metric("pm10", raw_data["pm10_ug_m3"], "µg/m³")

        # --- Caso D: rest.level.v1 (Water Tank) ---
        elif schema_family == "rest.level.v1":
            if "level_pct" in raw_data: add_metric("level_pct", raw_data["level_pct"], "%")
            if "level_liters" in raw_data: add_metric("level_liters", raw_data["level_liters"], "L")

        # --- Caso E: topic.power.v1 (Solar Array, Power Bus, Power Consumption) ---
        elif schema_family == "topic.power.v1":

            
            if "power_kw" in raw_data: add_metric("power_kw", raw_data["power_kw"], "kW")
            if "voltage_v" in raw_data: add_metric("voltage_v", raw_data["voltage_v"], "V")
            if "current_a" in raw_data: add_metric("current_a", raw_data["current_a"], "A")
            if "cumulative_kwh" in raw_data: add_metric("cumulative_kwh", raw_data["cumulative_kwh"], "kWh")

        # --- Caso F: topic.thermal_loop.v1 ---
        elif schema_family == "topic.thermal_loop.v1":
            if "temperature_c" in raw_data: add_metric("temperature", raw_data["temperature_c"], "°C")
            if "flow_l_min" in raw_data: add_metric("flow", raw_data["flow_l_min"], "L/min")

        # --- Caso G: topic.airlock.v1 ---
        elif schema_family == "topic.airlock.v1":
            airlock_state = raw_data.get("last_state", "UNKNOWN")
            
            if "cycles_per_hour" in raw_data: 
                add_metric("cycles_per_hour", raw_data["cycles_per_hour"], "cycles/h", possible_status=airlock_state)

    except (ValueError, TypeError) as e:
        print(f"❌ Errore di parsing su {final_id}: {e}")

    if results:
        for r in results:
            print(f"   -> {r.model_dump()}", flush=True)

    return results

def to_json(data: StandardFormat) -> str:
    return data.model_dump_json()