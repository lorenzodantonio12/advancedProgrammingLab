import crud
from models import StandardFormat
from cache import latest_sensor_state, latest_actuator_state
from broker_client import BrokerClient

command_broker = BrokerClient(host='activemq') # 'activemq' su Docker
try:
    command_broker.connect()
except Exception as e:
    print("Avviso: Broker per i comandi non ancora connesso.")

def receive_event(event: StandardFormat):

    latest_sensor_state[event.id] = event
    print("memoria aggiornata")
    
    rules = crud.get_rules()


    print(event.value, event.metric, event.id)

    for r in rules:

        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")
        print("sto cercando le regole")

        print(r.sensor_name, event.id, r.metric, event.metric)
        print(r.sensor_name, event.id, r.metric, event.metric)
        print(r.sensor_name, event.id, r.metric, event.metric)
        print(r.sensor_name, event.id, r.metric, event.metric)
        print(r.sensor_name, event.id, r.metric, event.metric)
        print(r.sensor_name, event.id, r.metric, event.metric)
        print(r.sensor_name, event.id, r.metric, event.metric)
        print(r.sensor_name, event.id, r.metric, event.metric)

        if (r.sensor_name == event.id and r.metric == event.metric):

            print("sono dentro all'if!!!")
            print("sono dentro all'if!!!")
            print("sono dentro all'if!!!")
            print("sono dentro all'if!!!")
            print("sono dentro all'if!!!")
            print("sono dentro all'if!!!")
            print("sono dentro all'if!!!")
            print("sono dentro all'if!!!")
            print("sono dentro all'if!!!")

            condition = False

            if (r.operator == '<' and event.value < r.value):
                condition = True
            elif (r.operator == '<=' and event.value <= r.value):
                condition = True
            elif (r.operator == '=' and event.value == r.value):
                condition = True
            elif (r.operator == '>' and event.value > r.value):
                condition = True
            elif (r.operator == '>=' and event.value >= r.value):
                condition = True
            
            if condition:
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")
                print(f"rule {r.id_rule} is now active!!")

                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")
                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")

                trigger_actuator(r.actuator_name, r.state)
    

def trigger_actuator(name: str, state: str):
    print(f"sending to actuator {name} command {state}")

    if latest_actuator_state[name] == state:
        return

    message = f'{{"actuator": "{name}", "state": "{state}"}}'

    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")
    print(f"mandato messaggio: {name}, {state}")

    if command_broker.connected:
        command_broker.send_message("actuator_command", message)

        latest_actuator_state[name] = state

        print(f"stato di {name} cambiato a {state}")
    else:
        print("broker non connesso")
