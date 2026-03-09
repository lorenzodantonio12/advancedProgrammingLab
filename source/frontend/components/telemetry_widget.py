from nicegui import ui

def TelemetryWidget(title: str, icon_name: str, color: str):
    # 🟢 MODIFICA QUI: Cambiato h-48 in h-64 (circa 256px di altezza). 
    # Se li vuoi ancora più giganti puoi mettere h-72 o h-80!
    with ui.card().classes('h-72 w-72 items-center shadow-lg p-4 border-t-4 flex-col').style(f'border-color: {color}'):
        
        # Header con icona e pallino LIVE lampeggiante
        with ui.row().classes('w-full justify-between items-start'):
            ui.icon(icon_name, size='2em', color=color)
            ui.icon('circle', size='1em', color='green').classes('animate-pulse')
            
        ui.label(title).classes('text-md font-bold text-gray-700 text-center w-full leading-tight')
        
        # Contenitore dati: l'altezza extra darà molto più respiro a questa lista
        data_container = ui.column().classes('w-full items-center justify-start flex-grow overflow-y-auto scrollbar-hide mt-2 gap-1')
        
        # Dizionario interno per salvare i riferimenti alle label
        labels = {}

        def update_data(data):
            if not isinstance(data, dict):
                return

            for key, val in data.items():
                
                # Creazione dinamica delle righe
                if key not in labels:
                    with data_container:
                        with ui.row().classes('w-full justify-between items-center border-b border-gray-100 pb-1'):
                            ui.label(key).classes('text-xs font-semibold text-gray-400 uppercase')
                            labels[key] = ui.label('---').classes('text-md font-bold text-gray-800 text-right')

                # Logica colori e allarmi
                text_color = 'text-gray-800'
                is_pulsing = False
                
                if str(val).upper() in ["PRESSURIZING", "DEPRESSURIZING", "DANGER", "CRITICAL"]:
                    text_color = 'text-red-500'
                    is_pulsing = True
                
                # Aggiornamento
                labels[key].set_text(str(val))
                labels[key].classes(replace=f'text-md font-bold {text_color} text-right')
                
                if is_pulsing:
                    labels[key].classes(add='animate-pulse')
                else:
                    labels[key].classes(remove='animate-pulse')

        return update_data