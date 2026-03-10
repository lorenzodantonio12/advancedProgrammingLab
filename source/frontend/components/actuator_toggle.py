from nicegui import ui
from services.api import set_actuator_state

class ActuatorWidget:
    def __init__(self, name, icon, color, actuator_id, initial_state):
        self.name = name
        self.actuator_id = actuator_id
        
        start_val = (initial_state == 'ON')

        with ui.card().classes('p-4 shadow-lg items-center w-44 flex-col gap-1'):
            ui.icon(icon, color=color).classes('text-4xl mb-1')
            ui.label(name).classes('text-xs text-gray-500 uppercase tracking-wider text-center h-8')
            
            self.switch = ui.switch(value=start_val)
            
            async def handle_toggle():
                new_state = 'ON' if self.switch.value else 'OFF'
                success = set_actuator_state(self.actuator_id, new_state)
                if success:
                    kolor = 'positive' if new_state == 'ON' else 'negative'
                    ui.notify(f"Manual: {self.name} -> {new_state}", color=kolor)
                else:
                    ui.notify(f"Error: {self.name} failed", color='negative')
                    self.switch.value = not self.switch.value

            self.switch.on('click', handle_toggle)

    def update_from_rule(self, new_state_str: str):
        target_bool = (new_state_str == 'ON')
        if self.switch.value != target_bool:
            self.switch.value = target_bool
            ui.notify(f"Automation: {self.name} -> {new_state_str}", color='warning', icon='bolt')