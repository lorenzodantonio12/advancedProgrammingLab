from nicegui import ui

def apply_status_color(badge, status):
    if not status:
        badge.set_visibility(False)
        return
    
    badge.set_visibility(True)
    badge.set_text(status)
    
    badge.classes(replace='text-[11px] font-bold px-2 py-1 rounded w-full text-center mt-2 tracking-wide')
    
    if status in ['OK', 'ok', 'IDLE']:
        badge.classes(add='bg-green-100 text-green-700')
    elif status in ['PRESSURIZING', 'DEPRESSURIZING']:
        badge.classes(add='bg-blue-100 text-blue-700 animate-pulse')
    elif status in ['WARNING', 'warning']:
        badge.classes(add='bg-red-100 text-red-700 animate-pulse')
    else:
        badge.classes(add='bg-gray-100 text-gray-700')

class SensorWidget:
    def __init__(self, name, icon, color):
        self.name = name
        
        with ui.card().classes('p-4 shadow-lg items-center w-52 h-48 flex-col gap-2'):
            ui.icon(icon, color=color).classes('text-4xl')
            ui.label(name).classes('text-xs text-gray-500 uppercase tracking-wider text-center h-8')
            
            # mt-auto spinge il numero in fondo alla card, tenendo tutto allineato
            self.value_label = ui.label('--').classes('text-2xl font-bold text-gray-800 mt-auto')

            self.status_badge = ui.label('OK').classes('text-[11px] font-bold px-2 py-1 rounded bg-green-100 text-green-700 w-full text-center mt-2 tracking-wide')
            self.status_badge.set_visibility(False)

    def __call__(self, value_str, status = 'OK'):
        self.value_label.set_text(value_str)
        apply_status_color(self.status_badge, status)

class MultiSensorWidget:
    def __init__(self, name, icon, color):
        self.name = name
        self.metrics = {}
        
        with ui.card().classes('p-4 shadow-lg items-center w-60 h-48 flex-col gap-1'):
            ui.icon(icon, color=color).classes('text-4xl')
            ui.label(name).classes('text-xs text-gray-500 uppercase tracking-wider text-center h-8')
            
            self.container = ui.column().classes('w-full items-center gap-1 mt-auto')

            self.status_badge = ui.label('OK').classes('text-[11px] font-bold px-2 py-1 rounded bg-green-100 text-green-700 w-full text-center mt-2 tracking-wide')
            self.status_badge.set_visibility(False)

    def __call__(self, metric_name, value_str, status = 'OK'):
        self.metrics[metric_name] = value_str
        apply_status_color(self.status_badge, status)
        
        self.container.clear()
        with self.container:
            for k, v in self.metrics.items():
                label = k.replace('_', ' ').title()
                with ui.row().classes('w-full justify-between items-center text-xs border-b border-gray-100 pb-1'):
                    ui.label(label).classes('text-gray-500')
                    ui.label(v).classes('font-bold text-gray-800')