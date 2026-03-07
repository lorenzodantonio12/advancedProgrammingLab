from nicegui import ui

class SensorWidget:
    def __init__(self, name, icon, color):
        with ui.card().classes('p-4 shadow-lg items-center w-40'):
            ui.icon(icon, color=color).classes('text-4xl')
            ui.label(name).classes('text-sm text-gray-500')
            # Creiamo la label una volta sola e la salviamo come variabile della classe
            self.value_label = ui.label('---').classes('text-2xl font-bold')

    def __call__(self, data):
        """Metodo chiamato per aggiornare il valore"""
        # Cambiamo solo il testo, NON creiamo un nuovo ui.label()
        self.value_label.set_text(str(data))