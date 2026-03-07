import random
import time
from normalizer import map_to_standard
from broker_client import BrokerClient

# Mappa topic -> (sensor_id, schema_family, raw_data_generator)
TELEMETRY_STREAMS = [
    ("mars/telemetry/solar_array", "solar_array", "topic.power.v1", lambda: {"power_kw": round(random.uniform(10.0, 15.0), 1)}),
    ("mars/telemetry/power_bus", "power_bus", "topic.power.v1", lambda: {"power_kw": round(random.uniform(8.0, 10.0), 1)}),
    ("mars/telemetry/power_consumption", "power_consumption", "topic.power.v1", lambda: {"power_kw": round(random.uniform(5.0, 7.0), 1)}),
    ("mars/telemetry/radiation", "radiation", "topic.environment.v1", lambda: {"radiation": round(random.uniform(0.1, 0.5), 3)}),
    ("mars/telemetry/life_support", "life_support", "topic.environment.v1", lambda: {"o2_reserve": round(random.uniform(80, 100), 1)}),
    ("mars/telemetry/thermal_loop", "thermal_loop", "topic.thermal_loop.v1", lambda: {"temperature_c": round(random.uniform(-10.0, -5.0), 1)}),
    ("mars/telemetry/airlock", "airlock", "topic.airlock.v1", lambda: {"cycles_per_hour": round(random.uniform(0, 2), 1)}),
]

def start_streaming():
    broker = BrokerClient(host='activemq')
    broker.connect()
    
    print("Avvio generazione Telemetria (7 topic)...")
    
    while True:
        try:
            for topic, sensor_id, schema_family, data_gen in TELEMETRY_STREAMS:
                raw_data = data_gen()
                standard_data = map_to_standard(sensor_id, raw_data, schema_family)
                print(f"STREAM -> {standard_data.id}: {standard_data.value} {standard_data.unit}")
                broker.send_message("mars_telemetry", standard_data.model_dump_json())
            
            print("-" * 50)
            time.sleep(5)
        except Exception as e:
            print(f"Errore nella generazione stream: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_streaming()