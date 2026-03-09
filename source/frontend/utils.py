def extract_telemetry_data(t_data):
    """Estrae i dati in un formato dizionario {Etichetta: Valore} per i widget telemetria"""
    ui_data = {}
    if all(k in t_data for k in ['metric', 'value']):
        label = t_data["metric"].replace('_', ' ').title()
        unit = t_data.get('unit', '')
        ui_data[label] = f"{t_data['value']} {unit}".strip()
    elif "measurements" in t_data:
        for m in t_data["measurements"]:
            label = m['metric'].replace('_', ' ').title()
            ui_data[label] = f"{m['value']} {m.get('unit', '')}".strip()
    else:
        for k, v in t_data.items():
            if k not in ['id', 'topic', 'timestamp', 'origin', 'status']:
                label = k.replace('_', ' ').title()
                ui_data[label] = str(v)
    return ui_data