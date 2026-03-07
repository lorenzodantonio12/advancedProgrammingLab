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
        print(f"Ricevuto messaggio dal broker: {body[:60]}...")
        
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
            
            # Iscriviti alla coda dove Persona 1 sta scrivendo
            conn.subscribe(destination=f'/queue/{queue_name}', id=1, ack='auto')
            
            connected = True
            print(f"In ascolto sulla coda /queue/{queue_name}...")
        except Exception as e:
            print(f"Broker non pronto, riprovo tra 3 secondi... ({e})")
            time.sleep(3)
            
    # Tieni in vita il processo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Disconnessione dal broker...")
        conn.disconnect()

if __name__ == "__main__":
    start_listening(host='localhost')

