import stomp
import json
import time
import os
from actuator_client import trigger_actuator

class ActuatorListener(stomp.ConnectionListener):
    def on_message(self, frame):
        try:
            command = json.loads(frame.body)
            # Ci aspettiamo un JSON tipo {"actuator": "cooling_fan", "state": "ON"}
            actuator_id = command["actuator"]
            state = command["state"]
            
            trigger_actuator(actuator_id, state)
        except Exception as e:
            print(f"❌ Errore processamento comando: {e}")

def start_listening():
    # Prendi l'host del broker dall'ambiente (default: activemq)
    host = os.getenv("BROKER_HOST", "activemq")
    port = 61613
    
    conn = stomp.Connection([(host, port)])
    conn.set_listener('actuator_listener', ActuatorListener())
    
    while True:
        try:
            conn.connect(wait=True)
            conn.subscribe(destination='/queue/actuator_command', id=1, ack='auto')
            print(f"📡 Consumer in ascolto su {host}:61613 (coda: actuator_command)")
            break
        except Exception:
            print("⏳ Broker non pronto, riprovo tra 2s...")
            time.sleep(2)

    # Loop infinito per mantenere il container attivo
    while True:
        time.sleep(10)

if __name__ == "__main__":
    start_listening()