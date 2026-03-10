import asyncio
import stomp
import json
import threading
import time
import requests
from models.scheme import StandardFormat

# --- CONFIGURAZIONE ---
BROKER_HOST = 'activemq'
BROKER_PORT = 61613
AUTOMATION_URL = "http://automation:8000"

# Coda asincrona per i messaggi WebSocket
telemetry_queue = asyncio.Queue()

# Dizionario in memoria per i dati più recenti
latest_sensor_data = {}

class TelemetryListener(stomp.ConnectionListener):
    def __init__(self, loop):
        self.loop = loop

    def on_error(self, frame):
        print(f"[BROKER ERROR] {frame.body}")

    def on_message(self, frame):
        try:
            data = json.loads(frame.body)
            event = StandardFormat(**data)
            
            # Aggiorna cache locale
            key = f"{event.id}_{event.metric}" 
            latest_sensor_data[key] = event
            
            if self.loop:
                self.loop.call_soon_threadsafe(telemetry_queue.put_nowait, event.model_dump())
        except Exception as e:
            print(f"Errore elaborazione messaggio: {e}")

def start_telemetry_consumer(loop):
    conn = stomp.Connection([(BROKER_HOST, BROKER_PORT)])
    conn.set_listener('', TelemetryListener(loop))
    while True:
        try:
            if not conn.is_connected():
                conn.connect(wait=True)
                conn.subscribe(destination='/topic/mars_telemetry', id=1, ack='auto')
                print(f"✓ Frontend connesso ad ActiveMQ")
            time.sleep(5)
        except Exception:
            time.sleep(2)

# --- FUNZIONI PER IL FRONTEND ---

async def get_next_push_event():
    return await telemetry_queue.get()

def get_latest_sensor_data():
    return [event.model_dump() for event in latest_sensor_data.values()]

def get_initial_actuators_state():
    actuators = ['cooling_fan', 'entrance_humidifier', 'hall_ventilation', 'habitat_heater']
    fallback_state = {act_id: 'OFF' for act_id in actuators}
    
    try:
        url = f"{AUTOMATION_URL.rstrip('/')}/api/get-actuator-state"
        r = requests.get(url, timeout=2)
        
        if r.status_code == 200:
            data = r.json()
            if data:
                return data
                
    except Exception as e:
        print(f"⚠️ Errore recupero stati attuatori, uso il fallback a OFF. Dettaglio: {e}", flush=True)
        
    return fallback_state

def set_actuator_state(actuator_id: str, state: str):
    try:
        r = requests.post(
            f"{AUTOMATION_URL}/api/set-actuator", 
            params={"actuator_id": actuator_id, "state": state}, 
            timeout=1
        )
        return r.status_code == 200
    except Exception:
        return False

# --- REGOLE ---

def get_rules():
    try:
        response = requests.get(f"{AUTOMATION_URL}/api/get-rules", timeout=1)
        return response.json() if response.status_code == 200 else []
    except Exception:
        return []

def add_rule(sensor, metric, operator, value, actuator, action):
    rule = {
        "sensor_name": sensor, "metric": metric, "operator": operator, "value": float(value),
        "actuator_name": actuator, "state": action
    }
    try:
        r = requests.post(f"{AUTOMATION_URL}/api/create-rule", json=rule, timeout=1)
        return r.status_code == 200
    except Exception: return False

def edit_rule(rule_id, update_data):
    """Invia al backend i campi modificati della regola"""
    try:
        r = requests.patch(f"{AUTOMATION_URL}/api/update-rule/{rule_id}", json=update_data, timeout=1)
        if r.status_code == 200:
            return True, "success"
        elif r.status_code == 409: 
            return False, "conflict"
        elif r.status_code == 404: 
            return False, "not_found"
        else:
            return False, "error"
    except Exception: 
        return False


def delete_rule(rule_id):
    try:
        r = requests.delete(f"{AUTOMATION_URL}/api/delete-rule/{rule_id}", timeout=1)
        return r.status_code == 200
    except Exception: return False