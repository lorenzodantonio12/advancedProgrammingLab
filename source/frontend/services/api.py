import random
from datetime import datetime, timezone
from models.scheme import StandardFormat
import asyncio

# --- SIMULAZIONE DATABASE REGOLE ---
mock_rules_db = [
    {"id": 1, "sensor": "greenhouse_temperature", "operator": ">", "value": 28.0, "actuator": "cooling_fan", "action": "ON"}
]

# Coda simulata per i messaggi WebSocket
telemetry_queue = asyncio.Queue()

async def simulate_websocket_stream():
    """
    Simula un server che spinge dati via WebSocket ogni 5 secondi
    """
    while True:
        await asyncio.sleep(5)
        # Genera un dato a caso come se arrivasse dal bus di Marte
        data = get_telemetry_stream_mock() 
        await telemetry_queue.put(data)

async def get_next_push_event():
    return await telemetry_queue.get()

def get_rules():
    return mock_rules_db

def add_rule(sensor, operator, value, actuator, action):
    new_id = len(mock_rules_db) + 1 if mock_rules_db else 1
    new_rule = {
        "id": new_id,
        "sensor": sensor,
        "operator": operator,
        "value": float(value),
        "actuator": actuator,
        "action": action
    }
    mock_rules_db.append(new_rule)
    return True

def delete_rule(rule_id):
    global mock_rules_db
    mock_rules_db = [r for r in mock_rules_db if r["id"] != rule_id]
    return True

# --- API ATTUATORI ---
# In api.py, aggiorna lo stato iniziale
def get_initial_actuators_state():
    return {
        "cooling_fan": "OFF",
        "entrance_humidifier": "OFF",
        "hall_ventilation": "OFF",
        "habitat_heater": "OFF"
    }

# Assicurati che get_telemetry_stream_mock generi tutti i topic che hai messo in main.py

def set_actuator_state(actuator_id: str, state: str):
    print(f"[API FINTA] Inviato comando: {actuator_id} -> {state}")
    return True

# --- API SENSORI E TELEMETRIA (Con Modello Pydantic) ---

def get_latest_sensor_data():
    now = datetime.now(timezone.utc)
    events = []

    # Helper function per creare e dumpare l'evento
    def add_event(id, metric, val, unit, origin, status="ok"):
        event = StandardFormat(
            id=id, metric=metric, timestamp=now, value=val, unit=unit, origin=origin, status=status
        )
        events.append(event.model_dump()) # Usiamo .model_dump() o .dict() a seconda della versione di Pydantic

    # Sensori singoli
    add_event("greenhouse_temperature", "temperature", round(random.uniform(20.0, 30.0), 1), "°C", "rest.scalar.v1")
    add_event("entrance_humidity", "humidity", round(random.uniform(40.0, 60.0), 1), "%", "rest.scalar.v1")
    add_event("co2_hall", "co2", round(random.uniform(400, 800), 0), "ppm", "rest.scalar.v1")
    add_event("corridor_pressure", "pressure", round(random.uniform(980, 1020), 0), "hPa", "rest.scalar.v1")

    # Sensori multipli (es. PH genera 2 eventi separati col tuo modello)
    add_event("hydroponic_ph", "pH", round(random.uniform(5.5, 6.5), 2), "", "rest.chemistry.v1")
    add_event("hydroponic_ph", "EC", round(random.uniform(1.2, 2.0), 2), "mS/cm", "rest.chemistry.v1")

    add_event("air_quality_pm25", "pm1", round(random.uniform(1, 10), 1), "µg/m³", "rest.particulate.v1")
    add_event("air_quality_pm25", "pm25", round(random.uniform(5, 25), 1), "µg/m³", "rest.particulate.v1")
    add_event("air_quality_pm25", "pm10", round(random.uniform(10, 50), 1), "µg/m³", "rest.particulate.v1")

    add_event("air_quality_voc", "TVOC", round(random.uniform(50, 200), 0), "ppb", "rest.chemistry.v1")
    add_event("water_tank_level", "level_pct", round(random.uniform(10, 100), 1), "%", "rest.level.v1")
    add_event("water_tank_level", "level_liters", round(random.uniform(100, 1000), 0), "L", "rest.level.v1")

    return events

def get_telemetry_stream_mock():
    """
    Simula l'arrivo dei dati WebSocket rispettando alla lettera i contratti:
    topic.power.v1, topic.environment.v1, topic.thermal_loop.v1, topic.airlock.v1
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        # --- FAMIGLIA: topic.power.v1 ---
        "mars/telemetry/solar_array": {
            "topic": "mars/telemetry/solar_array", "event_time": now, "subsystem": "power_gen",
            "power_kw": round(random.uniform(10.0, 15.0), 1), "voltage_v": round(random.uniform(115, 125), 0),
            "current_a": round(random.uniform(90, 110), 1), "cumulative_kwh": 1050.5
        },
        "mars/telemetry/power_bus": {
            "topic": "mars/telemetry/power_bus", "event_time": now, "subsystem": "distribution",
            "power_kw": round(random.uniform(8.0, 10.0), 1), "voltage_v": 120.0,
            "current_a": round(random.uniform(60, 80), 1), "cumulative_kwh": 5200.0
        },
        "mars/telemetry/power_consumption": {
            "topic": "mars/telemetry/power_consumption", "event_time": now, "subsystem": "habitat",
            "power_kw": round(random.uniform(5.0, 7.0), 1), "voltage_v": 120.0,
            "current_a": round(random.uniform(40, 60), 1), "cumulative_kwh": 3100.0
        },

        # --- FAMIGLIA: topic.environment.v1 ---
        "mars/telemetry/radiation": {
            "topic": "mars/telemetry/radiation", "event_time": now, "status": "ok",
            "source": {"system": "external", "segment": "hull_top"},
            "measurements": [{"metric": "rad_level", "value": round(random.uniform(0.1, 0.5), 3), "unit": "mSv/h"}]
        },
        "mars/telemetry/life_support": {
            "topic": "mars/telemetry/life_support", "event_time": now, "status": "ok",
            "source": {"system": "internal", "segment": "habitat_a"},
            "measurements": [{"metric": "o2_reserve", "value": round(random.uniform(80, 100), 1), "unit": "%"}]
        },

        # --- FAMIGLIA: topic.thermal_loop.v1 ---
        "mars/telemetry/thermal_loop": {
            "topic": "mars/telemetry/thermal_loop", "event_time": now, "status": "ok",
            "loop": "primary_coolant", "temperature_c": round(random.uniform(-10.0, -5.0), 1),
            "flow_l_min": round(random.uniform(40.0, 50.0), 1)
        },

        # --- FAMIGLIA: topic.airlock.v1 ---
        "mars/telemetry/airlock": {
            "topic": "mars/telemetry/airlock", "event_time": now, 
            "airlock_id": "main_airlock_1", "cycles_per_hour": round(random.uniform(0, 2), 1),
            "last_state": random.choice(["IDLE", "IDLE", "PRESSURIZING", "DEPRESSURIZING"])
        }
    }