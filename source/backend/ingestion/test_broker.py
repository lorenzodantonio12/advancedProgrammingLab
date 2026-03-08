import stomp
import json
import time

class TelemetryListener(stomp.ConnectionListener):
    def on_message(self, frame):
        # Decodifica il JSON normalizzato
        data = json.loads(frame.body)
        print(f"📥 RICEVUTO: {data}")

def run_test_listener():
    # Usiamo localhost perché lo lanciamo da fuori Docker (il broker espone la 61613)
    conn = stomp.Connection([('localhost', 61613)])
    conn.set_listener('test_telemetry', TelemetryListener())
    
    try:
        conn.connect(wait=True)
        # Sottoscrizione alla coda della telemetria
        conn.subscribe(destination='/topic/mars_telemetry', id=1, ack='auto')
        print("Test Listener avviato! In attesa di dati da Poller e Stream...")
        print("Premi CTRL+C per fermare.\n" + "-"*50)
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        conn.disconnect()
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    run_test_listener()