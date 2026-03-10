import os
import requests

SIMULATOR_HOST = os.getenv("SIMULATOR_HOST", "simulator")
ACTUATOR_URL = f"http://{SIMULATOR_HOST}:8080/api/actuators"

def trigger_actuator(actuator_id: str, state: str):
    """Invia il comando POST al simulatore dentro la rete Docker"""
    try:
        payload = {"state": state}
        response = requests.post(f"{ACTUATOR_URL}/{actuator_id}", json=payload)
        
        if response.status_code == 200:
            print(f"[ACTUATOR] {actuator_id} impostato su {state}")
            return True
        else:
            print(f"[ACTUATOR] Errore su {actuator_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ [ACTUATOR] Connessione fallita verso {ACTUATOR_URL}")
        return False