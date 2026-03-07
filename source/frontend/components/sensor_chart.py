from nicegui import ui
import time

def SingleChartFactory(title: str, series_name: str, color: str, unit: str):
    """
    Crea un grafico Highcharts live per una singola metrica.
    Restituisce una funzione per aggiornare il grafico con un nuovo valore.
    """
    with ui.card().classes('w-full h-80 lg:h-96 shadow-lg bg-white rounded-xl p-4 mt-4'):
        chart = ui.highchart({
            'title': {'text': title},
            'chart': {'type': 'spline', 'backgroundColor': 'transparent'}, # 'spline' smussa le linee
            'xAxis': {'type': 'datetime', 'title': {'text': 'Tempo (Mars UTC)'}},
            'yAxis': {'title': {'text': f"{title} ({unit})"}, 'labels': {'format': '{value}' + unit}},
            'legend': {'enabled': False}, # Una sola serie, non serve la legenda
            'series': [{
                'name': series_name,
                'data': [],
                'color': color,
                'tooltip': {'valueSuffix': f" {unit}"}
            }],
        }).classes('w-full h-full')

    # Liste interne per mantenere lo storico (max 40 punti)
    history = []

    def update_chart(new_val):
        """Funzione restituita per l'aggiornamento live."""
        if new_val is not None:
            now_ts = time.time() * 1000 # Highcharts vuole millisecondi
            history.append([now_ts, new_val])
            
            # Mantieni lo storico leggero
            if len(history) > 40:
                history.pop(0)

            # Applichiamo i dati e aggiorniamo
            chart.options['series'][0]['data'] = history
            chart.update()

    return update_chart