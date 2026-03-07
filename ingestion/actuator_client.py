import requests

# URL base per gli attuatori nel simulatore come da specifica [cite: 32, 58]
ACTUATOR_URL = "http://simulator:8080/api/actuators"

def trigger_actuator(actuator_id: str, state: str):
    """
    Invia un comando POST a un attuatore marziano[cite: 57].
    
    Argomenti:
        actuator_id (str): ID dell'attuatore (es. 'cooling_fan', 'habitat_heater') [cite: 62, 65]
        state (str): Stato desiderato ('ON' o 'OFF') 
    """
    try:
        # Il bando richiede esplicitamente la chiave "state" 
        payload = {"state": state}
        
        # Endpoint: http://localhost:8080/api/actuators/{actuator_id} 
        response = requests.post(f"{ACTUATOR_URL}/{actuator_id}", json=payload)
        
        if response.status_code == 200:
            print(f"✅ [ACTUATOR] {actuator_id} impostato su {state}")
            return True
        else:
            print(f"❌ [ACTUATOR] Errore su {actuator_id}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ [ACTUATOR] Fallimento critico nella chiamata POST: {e}")
        return False