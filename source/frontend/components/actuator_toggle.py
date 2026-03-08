from nicegui import ui
from services.api import set_actuator_state

class ActuatorWidget:
    def __init__(self, name, icon, color, actuator_id, initial_state):
        self.name = name
        self.actuator_id = actuator_id
        
        with ui.card().classes('p-4 shadow-lg items-center w-44 flex-col gap-1'):
            ui.icon(icon, color=color).classes('text-4xl mb-1')
            ui.label(name).classes('text-xs text-gray-500 uppercase tracking-wider text-center h-8')
            
            # Proprietà reattiva per lo switch
            self.switch = ui.switch(value=(initial_state == 'ON'))
            
            # --- AZIONE MANUALE DELL'UTENTE ---
            async def handle_toggle():
                new_state = 'ON' if self.switch.value else 'OFF'
                success = set_actuator_state(self.actuator_id, new_state)
                
                if success:
                    ui.notify(f"Manuale: {self.name} -> {new_state}", color='positive')
                else:
                    ui.notify(f"Errore connessione {self.name}", color='negative')
                    # Se fallisce, annulliamo lo switch grafico
                    self.switch.value = not self.switch.value

            self.switch.on('click', handle_toggle)

    # --- AZIONE AUTOMATICA DAL MOTORE REGOLE ---
    def update_from_rule(self, new_state_str: str):
        """Metodo per aggiornare l'attuatore da codice (motore regole)"""
        target_bool = (new_state_str == 'ON')
        print(f"🛑 WIDGET ({self.name}): update_from_rule ricevuto! Stato grafico attuale: {self.switch.value}, Target richiesto: {target_bool}", flush=True)
        # Scatta SOLO se lo stato attuale è diverso, per non spammare le API
        if self.switch.value != target_bool:
            # 1. Aggiorna la grafica (NiceGUI reagisce subito a .value)
            self.switch.value = target_bool
            print(f"🛑 WIDGET ({self.name}): Sto cambiando l'interruttore!", flush=True)
            # 2. Invia il comando reale all'Automation via API
            set_actuator_state(self.actuator_id, new_state_str)
            
            # Notifica visiva per farti capire che è stata una regola
            ui.notify(f"⚡ Automazione: {self.name} -> {new_state_str}", color='warning')