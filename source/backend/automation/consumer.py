from models import StandardFormat
from automation_engine import receive_event
import stomp
import time
import json

class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print(f"Errore dal broker: {frame.body}")

    def on_message(self, frame):
        body = frame.body
        
        try:
            data_dict = json.loads(body)
            event = StandardFormat(**data_dict)
            
            receive_event(event)
        except Exception as e:
            print(f"Errore durante l'elaborazione dell'evento: {e}")

def start_listening(host='activemq', port=61613, queue_name='mars_telemetry'):
    conn = stomp.Connection([(host, port)])
    
    conn.set_listener('', MyListener())
    
    connected = False
    while not connected:
        try:
            print(f"Tentativo di connessione ad ActiveMQ (Consumer) su {host}:{port}...")
            conn.connect(wait=True)
            
            conn.subscribe(destination=f'/topic/{queue_name}', id=1, ack='auto')
            
            connected = True
            
            return conn
        
        except Exception as e:
            print(f"Broker non pronto, riprovo tra 3 secondi... ({e})")
            time.sleep(3)
            

