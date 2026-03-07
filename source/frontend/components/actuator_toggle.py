from nicegui import ui
from services.api import set_actuator_state

def ActuatorWidget(title: str, icon_name: str, color: str, actuator_id: str, initial_state: str = "OFF"):
    
    with ui.card().classes('h-64 w-64 items-center justify-between shadow-lg p-4'):
        # Header
        with ui.column().classes('items-center w-full gap-2'):
            ui.label(title).classes('text-lg font-bold text-gray-700 text-center leading-tight')
            status_icon = ui.icon(icon_name, size='3em')
            
        # Centro
        with ui.column().classes('w-full items-center justify-center flex-grow gap-2'):
            status_label = ui.label().classes('text-2xl font-bold')
            
            # Definiamo la funzione di cambio stato PRIMA dello switch
            def handle_change(e):
                new_val = e.value
                new_state_str = "ON" if new_val else "OFF"
                
                # 1. Update Grafico
                current_color = 'positive' if new_val else 'grey'
                status_icon.props(f'color={current_color}')
                status_label.set_text(new_state_str)
                status_label.classes(replace=f'text-2xl font-bold text-{current_color}')
                
                # 2. Notifica il Backend (API)
                set_actuator_state(actuator_id, new_state_str)

            # Creiamo lo switch collegando l'evento on_change
            is_on_init = (initial_state == "ON")
            switch = ui.switch(value=is_on_init, on_change=handle_change).classes('text-xl')
            
            # Inizializzazione manuale per il primo avvio
            handle_change(type('obj', (object,), {'value': is_on_init}))

    # QUESTA È LA FUNZIONE PER IL BOT (MOTORE REGOLE)
    def update_from_rules(new_state_str):
        target_bool = (new_state_str == "ON")
        # Cambiamo il valore dello switch: questo scatenerà AUTOMATICAMENTE handle_change
        if switch.value != target_bool:
            switch.value = target_bool

    return update_from_rules