import crud
from models import StandardFormat
from cache import latest_sensor_state

def receive_event(event: StandardFormat):

    print(latest_sensor_state)
    latest_sensor_state[event.id] = event
    print(latest_sensor_state)
    print("memoria aggiornata")
    
    rules = crud.get_rules()
    print(rules)


    print(event.value, event.metric, event.id)

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
                print(f"rule {r.id_rule} is now active!!")

                print(f"Motivo: {event.id} è {event.value} (Limite: {r.value})")

                trigger_actuator(r.actuator_name, r.state)
    
    print("fine elaborazione")

def trigger_actuator(name: str, state: str):
    print(f"actuator {name} is now {state}")


if __name__ == "__main__":
    # Immagina che la Persona 1 ti abbia appena inviato questo dato:
    class FakeEvent:
        id = "greenhouse_temperature"
        metric = "temperature"
        value = 35.5 # Fa caldissimo!

    evento_finto = FakeEvent()
    
    print("Elaborazione evento...")
    receive_event(evento_finto)