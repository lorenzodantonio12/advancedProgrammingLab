import crud
from models import StandardFormat
from cache import latest_sensor_state, latest_actuator_state
from broker_client import BrokerClient

command_broker = BrokerClient(host='activemq')
command_broker.connect()


def receive_event(event: StandardFormat):

    key = f"{event.id}_{event.metric}"

    latest_sensor_state[key] = event
    
    rules = crud.get_rules()

    for r in rules:

        if (r.sensor_name == event.id and r.metric == event.metric):

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


                trigger_actuator(r.actuator_name, r.state)
    

def trigger_actuator(name: str, state: str):

    if latest_actuator_state.get(name) == state:
        return

    message = f'{{"actuator": "{name}", "state": "{state}"}}'



    if command_broker.connected:
        command_broker.send_message("actuator_command", message)

        latest_actuator_state[name] = state

        print(f"stato di {name} cambiato a {state}")
    else:
        print("Broker non connesso")
