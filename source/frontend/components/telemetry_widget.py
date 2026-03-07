from nicegui import ui

def TelemetryWidget(title: str, icon_name: str, color: str):
    with ui.card().classes('h-64 w-64 items-center justify-between shadow-lg p-4 border-t-4').style(f'border-color: {color}'):
        
        # Header con icona e pallino LIVE lampeggiante
        with ui.row().classes('w-full justify-between items-start'):
            ui.icon(icon_name, size='2em', color=color)
            ui.icon('circle', size='1em', color='green').classes('animate-pulse')
            
        ui.label(title).classes('text-md font-bold text-gray-700 text-center w-full leading-tight')
        
        # Contenitore dati
        data_container = ui.column().classes('w-full items-center justify-center flex-grow')
        
    def update_data(data):
        data_container.clear()
        with data_container:
            if isinstance(data, dict):
                with ui.column().classes('w-full gap-2 mt-2'):
                    for key, val in data.items():
                        with ui.row().classes('w-full justify-between items-center border-b border-gray-100 pb-1'):
                            ui.label(key).classes('text-xs font-semibold text-gray-400 uppercase')
                            # Se è l'airlock e sta pressurizzando, mettiamo il testo in rosso o arancione
                            text_color = 'text-gray-800'
                            if val in ["PRESSURIZING", "DEPRESSURIZING"]:
                                text_color = 'text-red-500 animate-pulse'
                                
                            ui.label(str(val)).classes(f'text-md font-bold {text_color}')

    return update_data