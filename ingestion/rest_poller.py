import requests
import time
from normalizer import map_to_standard

# L'URL base del simulatore che hai appena testato [cite: 32]
BASE_URL = "http://localhost:8080/api/sensors"

# Lista completa degli 8 sensori con le loro famiglie di schema [cite: 41]
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
    print("Avvio del servizio di Polling REST... [Mission Mars 2036]")
    
    while True:
        for sensor_id, schema in SENSORS_TO_POLL:
            try:
                # 1. Richiesta al simulatore [cite: 37, 40]
                response = requests.get(f"{BASE_URL}/{sensor_id}")
                
                if response.status_code == 200:
                    raw_payload = response.json()
                    
                    # 2. Trasformazione usando il tuo Normalizer
                    standard_data = map_to_standard(sensor_id, raw_payload, schema)
                    
                    # 3. Stampa il risultato (per ora lo vediamo solo a terminale)
                    print(f"ID: {standard_data.id} | Valore: {standard_data.value} {standard_data.unit}")
                else:
                    print(f"Errore {response.status_code} per il sensore {sensor_id}")

            except Exception as e:
                print(f"Connessione fallita per {sensor_id}: {e}")
        
        # Attesa di 5 secondi come da requisiti 
        print("-" * 30)
        time.sleep(5)

if __name__ == "__main__":
    start_polling()