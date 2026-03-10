import stomp
import time

class BrokerClient:
    def __init__(self, host='activemq', port=61613):
        self.host = host
        self.port = port
        self.conn = stomp.Connection([(self.host, self.port)])
        self.connected = False

    def connect(self):
        while not self.connected:
            try:
                print(f"Tentativo di connessione ad ActiveMQ su {self.host}:{self.port}...")
                self.conn.connect(wait=True)
                self.connected = True
                print("Connesso ad ActiveMQ!")
            except Exception as e:
                print(f"Broker non pronto, riprovo tra 2 secondi... ({e})")
                time.sleep(2)
        return True

    def send_message(self, queue_name, message_json):
        try:
            self.conn.send(body=message_json, destination=f'/topic/{queue_name}')
            print(f" [SEND] -> Coda: {queue_name} | Data: {message_json[:50]}...")
        except Exception as e:
            print(f"Errore invio messaggio: {e}")

    def close(self):
        if self.connected:
            self.conn.disconnect()