import requests
import time
from normalizer import map_to_standard
from broker_client import BrokerClient

BASE_URL = "http://simulator:8080/api/sensors"

SENSORS_TO_POLL = [
    ("greenhouse_temperature", "rest.scalar.v1"),
    ("entrance_humidity", "rest.scalar.v1"),
    ("co2_hall", "rest.scalar.v1"),
    ("hydroponic_ph", "rest.chemistry.v1"),
    ("water_tank_level", "rest.level.v1"),
    ("corridor_pressure", "rest.scalar.v1"),
    ("air_quality_pm25", "rest.particulate.v1"),
    ("air_quality_voc", "rest.chemistry.v1")
]

def start_polling():
    # Inizializziamo il broker puntando al nome del servizio nel compose
    broker = BrokerClient(host='activemq') 
    broker.connect()

    while True:
        for sensor_id, schema in SENSORS_TO_POLL:
            try:
                response = requests.get(f"{BASE_URL}/{sensor_id}")
                if response.status_code == 200:
                    standard_data_list = map_to_standard(sensor_id, response.json(), schema)
                    
                    for standard_data in standard_data_list:
                        # 1. Stampa per controllo x
                        print(f"NORMALIZED: {standard_data.id} = {standard_data.value}")
                        
                        # 2. Invio al broker
                        broker.send_message("mars_telemetry", standard_data.model_dump_json())

            except Exception as e:
                print(f"Errore su {sensor_id}: {e}")
        
        print("-" * 50)
        time.sleep(5)

if __name__ == "__main__":
    start_polling()