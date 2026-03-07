from normalizer import map_to_standard
from broker_client import BrokerClient

# 1. Simuliamo un dato grezzo
raw = {"temp": 24.5}
standard_data = map_to_standard("greenhouse_temperature", raw, "rest.scalar.v1")

# 2. Proviamo a inviarlo (Nota: fallirà finché non lanciamo ActiveMQ)
try:
    client = BrokerClient()
    client.send_message("telemetry_queue", standard_data.model_dump_json())
    client.close()
except Exception as e:
    print(f"Errore previsto: {e}")
    print("TIP: Non abbiamo ancora acceso ActiveMQ, è normale!")