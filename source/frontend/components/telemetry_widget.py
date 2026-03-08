from nicegui import ui

def TelemetryWidget(title: str, icon_name: str, color: str):
    with ui.card().classes('h-64 w-64 items-center justify-between shadow-lg p-4 border-t-4').style(f'border-color: {color}'):
        
        # Header con icona e pallino LIVE lampeggiante
        with ui.row().classes('w-full justify-between items-start'):
            ui.icon(icon_name, size='2em', color=color)
            ui.icon('circle', size='1em', color='green').classes('animate-pulse')
            
        ui.label(title).classes('text-md font-bold text-gray-700 text-center w-full leading-tight')
        
        # Contenitore dati (vuoto all'inizio)
        data_container = ui.column().classes('w-full items-center justify-center flex-grow')
        
        # Dizionario interno per salvare i riferimenti alle label e non ricrearle
        labels = {}

        def update_data(data):
            #print(f"🛑 CHECK 3 (WIDGET {title}): Ricevuto -> {data}", flush=True)
            if not isinstance(data, dict):
                return

            # Se il container è vuoto (primo avvio), creiamo la struttura
            if not labels:
                data_container.clear()
                with data_container:
                    with ui.column().classes('w-full gap-2 mt-2'):
                        for key in data.keys():
                            with ui.row().classes('w-full justify-between items-center border-b border-gray-100 pb-1'):
                                ui.label(key).classes('text-xs font-semibold text-gray-400 uppercase')
                                # Salviamo il riferimento alla label del valore
                                labels[key] = ui.label('---').classes('text-md font-bold text-gray-800')

            # Aggiorniamo i valori senza distruggere i widget
            for key, val in data.items():
                if key in labels:
                    # Logica colori per Airlock o stati critici
                    text_color = 'text-gray-800'
                    is_pulsing = False
                    
                    if str(val) in ["PRESSURIZING", "DEPRESSURIZING", "DANGER", "CRITICAL"]:
                        text_color = 'text-red-500'
                        is_pulsing = True
                    
                    # Aggiorniamo testo e classi
                    labels[key].set_text(str(val))
                    labels[key].classes(replace=f'text-md font-bold {text_color}')
                    if is_pulsing:
                        labels[key].classes('animate-pulse')
                    else:
                        labels[key].classes(remove='animate-pulse')

        # IMPORTANTE: Restituiamo la funzione update_data definita DENTRO lo scope
        return update_data