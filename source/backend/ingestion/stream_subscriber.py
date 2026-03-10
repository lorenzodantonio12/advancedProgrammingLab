import requests
import json
import time
import threading
from normalizer import map_to_standard
from broker_client import BrokerClient

# Lista ufficiale dei topic dal bando (Pagina 3)
TOPICS = [
    "mars/telemetry/solar_array",
    "mars/telemetry/radiation",
    "mars/telemetry/life_support",
    "mars/telemetry/thermal_loop",
    "mars/telemetry/power_bus",
    "mars/telemetry/power_consumption",
    "mars/telemetry/airlock"
]

def listen_to_topic(topic, broker):
    # Endpoint SSE
    url = f"http://simulator:8080/api/telemetry/stream/{topic}"
    sensor_id = topic.replace("/", "_")
    
    schema_map = {
        "solar_array": "topic.power.v1",
        "radiation": "topic.environment.v1",
        "life_support": "topic.environment.v1",
        "thermal_loop": "topic.thermal_loop.v1",
        "power_bus": "topic.power.v1",
        "power_consumption": "topic.power.v1",
        "airlock": "topic.airlock.v1"
    }
    family = schema_map.get(topic.split('/')[-1], "topic.general.v1")

    while True:
        try:
            print(f"📡 Sottoscrizione a: {topic}")
            response = requests.get(url, stream=True, timeout=None)
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data:"):
                            json_str = decoded_line.replace("data:", "").strip()
                            raw_event = json.loads(json_str)
                            
                            # Normalizzazione
                            standard_data_list = map_to_standard(sensor_id, raw_event, family)

                            for standard_data in standard_data_list:
                            
                                # Log e invio al Broker (ActiveMQ)
                                print(f"📥 [STREAM] {sensor_id}: {standard_data.value} {standard_data.unit} \n")
                                broker.send_message("mars_telemetry", standard_data.model_dump_json())
            else:
                print(f"⚠️ Topic {topic} non disponibile (Status: {response.status_code})")
                time.sleep(10)
        except Exception as e:
            print(f"❌ Errore connessione su {topic}: {e}. Riprovo...")
            time.sleep(5)

def start_streaming():
    broker = BrokerClient(host='activemq')
    broker.connect()
    
    threads = []
    for t in TOPICS:
        thread = threading.Thread(target=listen_to_topic, args=(t, broker))
        thread.daemon = True # Il thread muore se il main muore
        thread.start()
        threads.append(thread)
    
    # Mantieni il processo attivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Spegnimento subscriber...")

if __name__ == "__main__":
    start_streaming()