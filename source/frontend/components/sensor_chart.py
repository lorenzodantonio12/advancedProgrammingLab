from nicegui import ui
import time

# --- LA MAGIA: Memoria Globale ---
# Questo dizionario vive finché il container Docker è acceso.
# Non muore mai al cambio pagina!
_GLOBAL_CHART_HISTORY = {}

def SingleChartFactory(title: str, series_name: str, color: str, unit: str):
    """
    Crea un grafico Highcharts live per una singola metrica.
    Restituisce una funzione per aggiornare il grafico con un nuovo valore.
    """
    
    # Se è la primissima volta che avviamo il server, creiamo la lista per questa serie.
    # Usiamo 'series_name' (es. 'Temp' o 'Humidity') come chiave unica.
    if series_name not in _GLOBAL_CHART_HISTORY:
        _GLOBAL_CHART_HISTORY[series_name] = []
        
    # Peschiamo lo storico salvato (se la pagina viene ricaricata, sarà pieno!)
    history = _GLOBAL_CHART_HISTORY[series_name]

    with ui.card().classes('w-full h-80 lg:h-96 shadow-lg bg-white rounded-xl p-4 mt-4'):
        chart = ui.highchart({
            'title': {'text': title},
            'chart': {'type': 'spline', 'backgroundColor': 'transparent'},
            'xAxis': {'type': 'datetime', 'title': {'text': 'Tempo (Mars UTC)'}},
            'yAxis': {'title': {'text': f"{title} ({unit})"}, 'labels': {'format': '{value}' + unit}},
            'legend': {'enabled': False},
            'series': [{
                'name': series_name,
                # PRECARICHIAMO I DATI! Quando torni sulla pagina, il grafico si disegna subito
                'data': list(history), 
                'color': color,
                'tooltip': {'valueSuffix': f" {unit}"}
            }],
        }).classes('w-full h-full')

    def update_chart(new_val):
        """Funzione restituita per l'aggiornamento live."""
        if new_val is not None:
            now_ts = time.time() * 1000 # Highcharts vuole millisecondi
            
            # Aggiungiamo il dato alla nostra lista globale
            history.append([now_ts, new_val])
            
            # Mantieni lo storico leggero (max 40 punti)
            if len(history) > 40:
                history.pop(0)

            # Applichiamo i dati aggiornati al grafico
            chart.options['series'][0]['data'] = history
            chart.update()

    return update_chart