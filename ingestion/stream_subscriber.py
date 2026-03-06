import requests
import json
import time
from normalizer import map_to_standard
from broker_client import BrokerClient

# In Docker, l'host è il nome del servizio nel compose
TOPIC_URL = "http://simulator:8080/api/telemetry/stream/mars/telemetry/radiation"

def start_streaming():
    broker = BrokerClient(host='activemq')
    broker.connect()
    
    print("Avvio sottoscrizione Telemetria (SSE)...")
    
    while True:
        try:
            response = requests.get(TOPIC_URL, stream=True, timeout=10)
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data:"):
                        json_str = decoded_line.replace("data:", "").strip()
                        raw_data = json.loads(json_str)
                        
                        # Normalizzazione
                        standard_data = map_to_standard("mars_radiation", raw_data, "topic.environment.v1")
                        
                        # Controllo a video e invio al broker
                        print(f"STREAM -> {standard_data.id}: {standard_data.value}")
                        broker.send_message("mars_telemetry", standard_data.model_dump_json())
        except Exception as e:
            print(f"Connessione stream persa, riprovo... ({e})")
            time.sleep(5)

if __name__ == "__main__":
    start_streaming()