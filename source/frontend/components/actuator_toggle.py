from nicegui import ui
# Importa set_actuator_state correttamente dal tuo percorso
from services.api import set_actuator_state 

def ActuatorWidget(name, icon, color, actuator_id, initial_state):
    with ui.card().classes('p-4 shadow-lg items-center'):
        ui.icon(icon, color=color).classes('text-4xl')
        ui.label(name).classes('text-lg font-bold')
        
        # Stato iniziale dello switch
        switch = ui.switch(value=(initial_state == 'ON'))
        
        # Definiamo l'azione separatamente
        async def handle_toggle():
            new_state = 'ON' if switch.value else 'OFF'
            # Chiamata API
            success = set_actuator_state(actuator_id, new_state)
            
            if success:
                # Usiamo ui.notify con esplicito posizionamento per stabilità
                ui.notify(f"{name}: {new_state}", color='positive')
            else:
                ui.notify(f"Errore controllo {name}", color='negative')
                # Se fallisce, torniamo indietro senza scatenare un loop
                switch.set_value(not switch.value)

        # Colleghiamo l'evento
        switch.on('click', handle_toggle) # Usiamo 'click' invece di 'on_change' per evitare loop infiniti se resettiamo il valore

    return switch