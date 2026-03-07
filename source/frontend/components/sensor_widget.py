from nicegui import ui

def SensorWidget(title: str, icon_name: str, color: str):
    # h-64 w-64 forzano la card a essere un quadrato perfetto di dimensioni fisse
    with ui.card().classes('h-64 w-64 items-center justify-between shadow-lg p-4'):
        
        # Header fisso in alto
        with ui.column().classes('items-center w-full gap-3'):
            ui.label(title).classes('text-lg font-bold text-gray-700 text-center leading-tight')
            ui.icon(icon_name, size='3em', color=color)
        
        # Contenitore dati al centro/basso, che occupa lo spazio rimanente
        data_container = ui.column().classes('w-full items-center justify-center flex-grow')
        
    def update_data(data):
        data_container.clear()
        with data_container:
            if isinstance(data, str):
                # Valore singolo: grande e centrato
                ui.label(data).classes('text-3xl font-bold')
                
            elif isinstance(data, dict):
                # Valori multipli: incolonnati
                with ui.column().classes('w-full gap-2'):
                    for key, val in data.items():
                        with ui.row().classes('w-full justify-between items-center'):
                            ui.label(key).classes('text-sm font-semibold text-gray-500')
                            ui.label(str(val)).classes('text-lg font-bold')
                            
            elif isinstance(data, list):
                # Array dinamico: incolonnati
                with ui.column().classes('w-full gap-2'):
                    for item in data:
                        with ui.row().classes('w-full justify-between items-center'):
                            ui.label(item.get('metric', '')).classes('text-sm font-semibold text-gray-500')
                            ui.label(f"{item.get('value', '')} {item.get('unit', '')}").classes('text-lg font-bold')

    return update_data