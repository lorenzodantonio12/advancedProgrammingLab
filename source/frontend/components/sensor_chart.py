from nicegui import ui
import time
from datetime import datetime

# Memoria globale per non perdere i dati quando cambi pagina
_GLOBAL_HISTORY = {}

def SingleChartFactory(title: str, series_name: str, color: str, unit: str):
    if series_name not in _GLOBAL_HISTORY:
        _GLOBAL_HISTORY[series_name] = []
    
    history = _GLOBAL_HISTORY[series_name]

    with ui.card().classes('w-full h-80 shadow-lg bg-white p-4 mt-4'):
        chart = ui.highchart({
            'title': {'text': title},
            'chart': {'type': 'spline', 'animation': False},
            'xAxis': {'type': 'datetime', 'title': {'text': 'Tempo'}},
            'yAxis': {'title': {'text': f"{series_name} ({unit})"}},
            'series': [{
                'name': series_name,
                'data': list(history), # Carica subito i dati esistenti
                'color': color,
            }],
        }).classes('w-full h-full')

    def update_chart(new_val, broker_timestamp=None):
        if new_val is None:
            return

        try:
            # --- 1. CONVERSIONE VALORE ---
            val_float = float(new_val)

            # --- 2. CONVERSIONE TEMPO ---
            if broker_timestamp:
                if isinstance(broker_timestamp, datetime):
                    now_ts = broker_timestamp.timestamp() * 1000
                elif isinstance(broker_timestamp, str):
                    dt_str = broker_timestamp.replace(' ', 'T').replace('Z', '')
                    now_ts = datetime.fromisoformat(dt_str.split('.')[0]).timestamp() * 1000
                else:
                    now_ts = float(broker_timestamp) * 1000 if float(broker_timestamp) < 1e11 else float(broker_timestamp)
            else:
                now_ts = time.time() * 1000

            # --- 3. AGGIORNAMENTO ---
            history.append([now_ts, val_float])
            history.sort(key=lambda x: x[0]) # Ordina per tempo

            if len(history) > 50:
                history.pop(0)

            chart.options['series'][0]['data'] = list(history)
            chart.update()

        except Exception as e:
            print(f"❌ Errore aggiornamento grafico {series_name}: {e}")

    return update_chart