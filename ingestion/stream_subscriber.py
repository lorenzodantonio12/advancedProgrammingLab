import requests
import json
from normalizer import map_to_standard

# URL per lo stream della radiazione (uno dei topic richiesti)
TOPIC_URL = "http://localhost:8080/api/telemetry/stream/mars/telemetry/radiation"

def start_streaming():
    print("Avvio sottoscrizione Telemetria (SSE)... [Monitoraggio Radiazioni]")
    
    # Usiamo stream=True per mantenere la connessione aperta
    try:
        response = requests.get(TOPIC_URL, stream=True)
        
        for line in response.iter_lines():
            if line:
                # Decodifichiamo la linea SSE (solitamente inizia con "data: ")
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data:"):
                    # Puliamo la stringa per avere solo il JSON
                    json_str = decoded_line.replace("data:", "").strip()
                    raw_data = json.loads(json_str)
                    
                    # Normalizziamo il dato della radiazione
                    # Usiamo 'topic.environment.v1' come indicato nella tabella del bando
                    standard_data = map_to_standard("mars_radiation", raw_data, "topic.environment.v1")
                    
                    print(f"STREAM -> ID: {standard_data.id} | Valore: {standard_data.value} mSv")

    except Exception as e:
        print(f"Errore nello stream: {e}")

if __name__ == "__main__":
    start_streaming()