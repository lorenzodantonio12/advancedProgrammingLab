import requests

# URL base per gli attuatori nel simulatore
ACTUATOR_URL = "http://simulator:8080/api/actuators"

def trigger_actuator(actuator_id: str, command: str):
    """
    Invia un comando a un attuatore.
    Esempio: actuator_id="cooling_fan", command="ON"
    """
    try:
        # Il bando richiede un POST con un payload tipo {"command": "ON"}
        payload = {"command": command}
        response = requests.post(f"{ACTUATOR_URL}/{actuator_id}", json=payload)
        
        if response.status_code == 200:
            print(f"✅ Comando {command} inviato a {actuator_id} con successo!")
        else:
            print(f"❌ Errore attuatore {actuator_id}: {response.status_code}")
    except Exception as e:
        print(f"❌ Fallimento critico attuatore: {e}")

# Esempio di test rapido
if __name__ == "__main__":
    # Test: accendiamo la ventola
    trigger_actuator("cooling_fan", "ON")