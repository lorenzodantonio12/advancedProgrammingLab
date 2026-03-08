import asyncio
from nicegui import ui

from components.sensor_widget import SensorWidget
from components.actuator_toggle import ActuatorWidget
from components.telemetry_widget import TelemetryWidget
from components.sensor_chart import SingleChartFactory
from services.api import (
    get_latest_sensor_data, get_initial_actuators_state, 
    get_rules, get_next_push_event
)

def extract_telemetry_data(t_data):
    """Estrae i dati in un formato dizionario SEMPLICE: {Etichetta: Valore}"""
    ui_data = {}
    
    # Se è il formato StandardFormat (id, metric, value, unit)
    if all(k in t_data for k in ['metric', 'value']):
        label = t_data["metric"].replace('_', ' ').title()
        unit = t_data.get('unit', '')
        ui_data[label] = f"{t_data['value']} {unit}".strip()
        
    # Se è il formato con misure multiple (measurements: [...])
    elif "measurements" in t_data:
        for m in t_data["measurements"]:
            label = m['metric'].replace('_', ' ').title()
            ui_data[label] = f"{m['value']} {m.get('unit', '')}".strip()
            
    # Se sono dati grezzi (power_kw, voltage_v, ecc.)
    else:
        for k, v in t_data.items():
            if k not in ['id', 'topic', 'timestamp', 'origin', 'status']:
                label = k.replace('_', ' ').title()
                ui_data[label] = str(v)
                
    return ui_data

def setup_dashboard_page(navigation_bar_func):
    @ui.page('/')
    async def dashboard_page():
        # Renderizza la barra di navigazione
        navigation_bar_func()
        
        # --- 1. SENSORI AMBIENTALI ---
        ui.label('Environmental Sensors').classes('text-2xl font-bold w-full text-center mt-6 text-gray-800')
        sensor_updaters = {}
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            sensor_updaters['greenhouse_temperature'] = SensorWidget('Greenhouse Temp', 'thermostat', 'red')
            sensor_updaters['entrance_humidity'] = SensorWidget('Entrance Humidity', 'water_drop', 'blue')
            sensor_updaters['co2_hall'] = SensorWidget('Corridor CO2', 'co2', 'green')
            sensor_updaters['corridor_pressure'] = SensorWidget('Corridor Pressure', 'compress', 'purple')
            sensor_updaters['hydroponic_ph'] = SensorWidget('Hydroponic pH', 'science', 'teal')
            sensor_updaters['air_quality_voc'] = SensorWidget('Air Quality VOC', 'air', 'orange')
            sensor_updaters['air_quality_pm25'] = SensorWidget('Air Quality PM2.5', 'blur_on', 'grey')
            sensor_updaters['water_tank_level'] = SensorWidget('Water Tank Level', 'waves', 'cyan')

        # --- 2. GRAFICI ---
        with ui.row().classes('w-full gap-4 p-4 justify-center flex-wrap lg:flex-nowrap'):
            update_temp_chart = SingleChartFactory('Temperature Trend', 'Temp', '#ef4444', '°C')
            update_hum_chart = SingleChartFactory('Humidity Trend', 'Humidity', '#3b82f6', '%')

        # --- 3. ATTUATORI ---
        ui.label('Actuators Control').classes('text-2xl font-bold w-full text-center mt-8 text-gray-800')
        act_states = get_initial_actuators_state()
        act_updaters = {}
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            act_updaters['cooling_fan'] = ActuatorWidget('Cooling Fan', 'ac_unit', 'blue', 'cooling_fan', act_states.get('cooling_fan'))
            act_updaters['entrance_humidifier'] = ActuatorWidget('Humidifier', 'water_drop', 'cyan', 'entrance_humidifier', act_states.get('entrance_humidifier'))
            act_updaters['hall_ventilation'] = ActuatorWidget('Ventilation', 'air', 'teal', 'hall_ventilation', act_states.get('hall_ventilation'))
            act_updaters['habitat_heater'] = ActuatorWidget('Heater', 'fireplace', 'orange', 'habitat_heater', act_states.get('habitat_heater'))

        # --- 4. TELEMETRIA ---
        ui.label('Live Telemetry (WebSocket)').classes('text-2xl font-bold w-full text-center mt-8 text-gray-800')
        tel_updaters = {}
        tel_defs = {
            'mars/telemetry/solar_array': ('Solar Panels', 'solar_power', '#ff9900'),
            'mars/telemetry/power_bus': ('Power Bus', 'electrical_services', '#ffcc00'),
            'mars/telemetry/power_consumption': ('Power Consumption', 'electric_bolt', '#ff0000'),
            'mars/telemetry/radiation': ('Radiation', 'radar', '#aa00ff'),
            'mars/telemetry/life_support': ('Life Support', 'favorite', '#00cc00'),
            'mars/telemetry/thermal_loop': ('Thermal Loop', 'severe_cold', '#0066ff'),
            'mars/telemetry/airlock': ('Airlock', 'meeting_room', '#999999'),
        }
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            for topic, (name, icon, col) in tel_defs.items():
                tel_updaters[topic] = TelemetryWidget(name, icon, col)

        # --- LOGICA 1: REST POLLING (Dati Lenti + Regole) ---
        def update_rest_data():
            # print("⏱️ [TIMER] Tick! La funzione è partita...", flush=True) # Decommenta se vuoi vederlo sempre
            try:
                raw = get_latest_sensor_data()
                
                if not raw:
                    print("⚠️ [ATTENZIONE] Nessun dato sensore disponibile. Salto le regole.", flush=True)
                    return

                # 1. Raggruppamento dati e aggiornamento Widget Sensori
                grouped = {}
                for e in raw:
                    sid = e['id']
                    if sid not in grouped: 
                        grouped[sid] = []
                    grouped[sid].append(e)
                    
                    if sid in sensor_updaters:
                        sensor_updaters[sid](f"{e['value']} {e.get('unit', '')}")

                # 2. Update Grafici Highcharts
                t = next((e['value'] for e in raw if e['id'] == 'greenhouse_temperature'), None)
                h = next((e['value'] for e in raw if e['id'] == 'entrance_humidity'), None)
                update_temp_chart(t)
                update_hum_chart(h)

                # 3. Motore Regole (Allineato con l'API del Backend)
                rules = get_rules()
                
                if not isinstance(rules, list):
                    print(f"❌ [ERRORE API] get_rules non ha restituito una lista! Ricevuto: {rules}", flush=True)
                    return

                for rule in rules:
                    # ORA USIAMO LE CHIAVI ESATTE DEL BACKEND
                    sensor_name = rule.get('sensor_name')
                    
                    if not sensor_name:
                        print(f"⚠️ [WARNING] Regola ignorata perché manca 'sensor_name': {rule}", flush=True)
                        continue 
                        
                    if sensor_name in grouped:
                        val = float(grouped[sensor_name][0]['value'])
                        target = float(rule.get('value', 0))
                        op = rule.get('operator')
                        trigger = False
                        
                        # Valutazione della logica
                        if op == '>': trigger = val > target
                        elif op == '<': trigger = val < target
                        elif op == '>=': trigger = val >= target
                        elif op == '<=': trigger = val <= target
                        elif op == '=': trigger = val == target
                        
                        print(f"🛑 REGOLE: Valuto {sensor_name} ({val}) {op} {target} -> SCATTA? {trigger}", flush=True)
                        
                        # USIAMO LE CHIAVI ESATTE DEL BACKEND PER ATTUATORE E STATO
                        actuator_name = rule.get('actuator_name')
                        action = rule.get('state') # Il backend lo chiama 'state' (ON/OFF)

                        # Se la regola è vera, invia il comando all'attuatore
                        if trigger and actuator_name in act_updaters:
                            print(f"⚡ TRIGGER! Aziono {actuator_name} -> {action}", flush=True)
                            act_updaters[actuator_name].update_from_rule(action)
                            
            except Exception as e:
                # Questo blocco è FONDAMENTALE per non far crashare tutto il timer se c'è un dato strano
                print(f"❌ [ERRORE FATALE] Errore durante update_rest_data: {e}", flush=True)
                
                
        # --- LOGICA 2: WEBSOCKET LISTENER (Dati Real-time) ---
        async def ws_listener():
            while True:
                try:
                    t_stream = await get_next_push_event()
                    #print(f"🛑 CHECK 2 (DASHBOARD): Pescato dalla coda -> {t_stream}", flush=True)
                    # Caso 1: Arriva un singolo evento (StandardFormat)
                    if isinstance(t_stream, dict) and 'id' in t_stream:
                        topic = f"mars/telemetry/{t_stream['id']}"
                        if topic in tel_updaters:
                            ui_data = extract_telemetry_data(t_stream)
                            tel_updaters[topic](ui_data)
                    # Caso 2: Arriva il blocco completo dei topic
                    elif isinstance(t_stream, dict):
                        for topic, data in t_stream.items():
                            if topic in tel_updaters:
                                tel_updaters[topic](extract_telemetry_data(data))
                except Exception as e:
                    print(f"WS Listener error: {e}")
                    await asyncio.sleep(1)

        # Avvio Timer (NiceGUI lo pulisce da solo alla disconnessione se creato qui)
        ui.timer(5.0, update_rest_data)
        
        # Avvio Task Asincrono per WebSocket
        bg_task = asyncio.create_task(ws_listener())
        
        # --- PULIZIA ALLA CHIUSURA (FIX CLIENT DELETED) ---
        ui.context.client.on_disconnect(lambda: bg_task.cancel())