from nicegui import ui

class SensorWidget:
    def __init__(self, name, icon, color):
        self.name = name
        
        # Aggiunto w-52 (larghezza) e h-48 (altezza fissa)
        with ui.card().classes('p-4 shadow-lg items-center w-52 h-48 flex-col gap-2'):
            ui.icon(icon, color=color).classes('text-4xl')
            ui.label(name).classes('text-xs text-gray-500 uppercase tracking-wider text-center h-8')
            
            # mt-auto spinge il numero in fondo alla card, tenendo tutto allineato
            self.value_label = ui.label('--').classes('text-2xl font-bold text-gray-800 mt-auto')

    def __call__(self, value_str):
        self.value_label.set_text(value_str)

class MultiSensorWidget:
    def __init__(self, name, icon, color):
        self.name = name
        self.metrics = {}
        
        # Stessa altezza (h-48) e larghezza leggermente maggiore (w-60) per farci stare le scritte lunghe
        with ui.card().classes('p-4 shadow-lg items-center w-60 h-48 flex-col gap-1'):
            ui.icon(icon, color=color).classes('text-4xl')
            ui.label(name).classes('text-xs text-gray-500 uppercase tracking-wider text-center h-8')
            
            # mt-auto spinge la lista in basso
            self.container = ui.column().classes('w-full items-center gap-1 mt-auto')

    def __call__(self, metric_name, value_str):
        self.metrics[metric_name] = value_str
        
        self.container.clear()
        with self.container:
            for k, v in self.metrics.items():
                label = k.replace('_', ' ').title()
                with ui.row().classes('w-full justify-between items-center text-xs border-b border-gray-100 pb-1'):
                    ui.label(label).classes('text-gray-500')
                    ui.label(v).classes('font-bold text-gray-800')