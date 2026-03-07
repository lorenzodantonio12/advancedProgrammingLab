import stomp
import time

class BrokerClient:
    def __init__(self, host='activemq', port=61613):
        # Usiamo 'activemq' come host perché in Docker Compose i container 
        # si chiamano per nome, non 'localhost'
        self.host = host
        self.port = port
        self.conn = stomp.Connection([(self.host, self.port)])
        self.connected = False

    def connect(self):
        # Tentiamo la connessione finché non riusciamo
        while not self.connected:
            try:
                print(f"Tentativo di connessione ad ActiveMQ su {self.host}:{self.port}...")
                self.conn.connect(wait=True)
                self.connected = True
                print("✅ Connesso ad ActiveMQ!")
            except Exception as e:
                print(f"❌ Broker non pronto, riprovo tra 2 secondi... ({e})")
                time.sleep(2)
        return True

    def send_message(self, queue_name, message_json):
        try:
            self.conn.send(body=message_json, destination=f'/queue/{queue_name}')
            # Questo è quello che hai chiesto: stampa SEMPRE quando invia
            print(f" [SEND] -> Coda: {queue_name} | Data: {message_json[:50]}...")
        except Exception as e:
            print(f"⚠️ Errore invio messaggio: {e}")

    def close(self):
        if self.connected:
            self.conn.disconnect()