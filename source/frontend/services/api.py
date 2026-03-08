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
            #print(f"🛑 CHECK 1 (API): Arrivato da ActiveMQ -> {frame.body}", flush=True)
            data = json.loads(frame.body)
            event = StandardFormat(**data)
            
            # Aggiorna cache locale per REST polling
            key = f"{event.id}" 
            latest_sensor_data[key] = event
            
            # Inserimento sicuro nella coda per il WebSocket push
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
                print(f"✓ Frontend connesso ad ActiveMQ su {BROKER_HOST}")
            time.sleep(5)
        except Exception as e:
            print(f"⚠ ActiveMQ non pronto, riprovo tra 2s...")
            time.sleep(2)

# --- FUNZIONI PER IL FRONTEND (FIX IMPORT ERRORS) ---

async def get_next_push_event():
    """Il frontend resta in attesa qui via WebSocket"""
    return await telemetry_queue.get()

def get_latest_sensor_data():
    """Restituisce la lista di eventi per le card e i grafici"""
    return [event.model_dump() for event in latest_sensor_data.values()]

def get_telemetry_stream_mock():
    result = {}
    for event in latest_sensor_data.values():
        topic = f"mars/telemetry/{event.id}"
        # Formattazione per TelemetryWidget
        result[topic] = {
            "measurements": [
                {"metric": event.metric, "value": event.value, "unit": event.unit}
            ]
        }
    return result



# --- CHIAMATE ALL'AUTOMATION ENGINE ---

def get_rules():
    try:
        response = requests.get(f"{AUTOMATION_URL}/api/get-rules", timeout=2)
        return response.json() if response.status_code == 200 else []
    except Exception:
        return []

def add_rule(sensor, operator, value, actuator, action):
    rule = {
        "sensor_name": sensor, "operator": operator, "value": float(value),
        "actuator_name": actuator, "state": action, "metric": "cosa a caso che va cambiata" #da cambiare
    }
    try:
        r = requests.post(f"{AUTOMATION_URL}/api/create-rule", json=rule, timeout=2)
        return r.status_code == 200
    except Exception: return False

def delete_rule(rule_id):
    try:
        r = requests.delete(f"{AUTOMATION_URL}/api/delete-rule/{rule_id}", timeout=2)
        return r.status_code == 200
    except Exception: return False

_GLOBAL_ACTUATOR_STATE = {
    'cooling_fan': 'OFF',
    'entrance_humidifier': 'OFF',
    'hall_ventilation': 'OFF',
    'habitat_heater': 'OFF'
}

def get_initial_actuators_state():
    """Restituisce lo stato salvato nella memoria globale del frontend"""
    return _GLOBAL_ACTUATOR_STATE

def set_actuator_state(actuator_id: str, state: str):
    """Invia il comando al TUO backend e aggiorna la memoria"""
    try:
        # ECCOLA QUI: La TUA rotta esatta!
        r = requests.post(
            f"{AUTOMATION_URL}/api/set-actuator", 
            params={"actuator_id": actuator_id, "state": state}, 
            timeout=2
        )
        
        # Se il backend risponde "actuator set to ON/OFF" (status 200)
        if r.status_code == 200:
            # Salviamo l'informazione nella memoria globale
            _GLOBAL_ACTUATOR_STATE[actuator_id] = state
            print(f"✅ Comando inviato: {actuator_id} -> {state}", flush=True)
            return True
            
        print(f"❌ Errore backend: {r.status_code} - {r.text}", flush=True)
        return False
        
    except Exception as e:
        print(f"❌ Eccezione API set_actuator: {e}", flush=True)
        return False