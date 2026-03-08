import asyncio
from nicegui import ui
from components.sensor_widget import SensorWidget
from components.actuator_toggle import ActuatorWidget
from components.telemetry_widget import TelemetryWidget
from components.sensor_chart import SingleChartFactory
from services.api import (
    get_initial_actuators_state, 
    get_next_push_event, 
    get_rules,
    get_latest_sensor_data,
    set_actuator_state
)

def extract_telemetry_data(t_data):
    """Estrae i dati in un formato dizionario {Etichetta: Valore}"""
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

def setup_dashboard_page(navigation_bar_func):
    @ui.page('/')
    async def dashboard_page():
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

        # --- 3. ATTUATORI (Stato iniziale dal Backend) ---
        ui.label('Actuators Control').classes('text-2xl font-bold w-full text-center mt-8 text-gray-800')
        
        # Recupero lo stato reale dal backend all'avvio
        act_states = get_initial_actuators_state() or {}
        act_updaters = {}
        
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            act_updaters['cooling_fan'] = ActuatorWidget('Cooling Fan', 'ac_unit', 'blue', 'cooling_fan', act_states.get('cooling_fan', 'OFF'))
            act_updaters['entrance_humidifier'] = ActuatorWidget('Humidifier', 'water_drop', 'cyan', 'entrance_humidifier', act_states.get('entrance_humidifier', 'OFF'))
            act_updaters['hall_ventilation'] = ActuatorWidget('Ventilation', 'air', 'teal', 'hall_ventilation', act_states.get('hall_ventilation', 'OFF'))
            act_updaters['habitat_heater'] = ActuatorWidget('Heater', 'fireplace', 'orange', 'habitat_heater', act_states.get('habitat_heater', 'OFF'))

        # --- 4. TELEMETRIA ---
        ui.label('Live Telemetry').classes('text-2xl font-bold w-full text-center mt-8 text-gray-800')
        tel_updaters = {}
        tel_defs = {
            'solar_array': ('Solar Panels', 'solar_power', '#ff9900'),
            'power_bus': ('Power Bus', 'electrical_services', '#ffcc00'),
            'power_consumption': ('Power Consumption', 'electric_bolt', '#ff0000'),
            'radiation': ('Radiation', 'radar', '#aa00ff'),
            'life_support': ('Life Support', 'favorite', '#00cc00'),
            'thermal_loop': ('Thermal Loop', 'severe_cold', '#0066ff'),
            'airlock': ('Airlock', 'meeting_room', '#999999'),
        }
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            for eid, (name, icon, col) in tel_defs.items():
                topic = f"mars/telemetry/{eid}"
                tel_updaters[topic] = TelemetryWidget(name, icon, col)

        # --- 🚀 LOGICA CORE: WEBSOCKET + MOTORE REGOLE ---
        async def ws_listener():
            # BOOT: Riempie i grafici con i dati storici
            history = get_latest_sensor_data()
            if history:
                for h_ev in history:
                    h_id, h_val, h_ts = h_ev.get('id'), h_ev.get('value'), h_ev.get('timestamp')
                    if h_id == 'greenhouse_temperature': update_temp_chart(h_val, h_ts)
                    elif h_id == 'entrance_humidity': update_hum_chart(h_val, h_ts)

            while True:
                try:
                    t_stream = await get_next_push_event()
                    if not t_stream: continue
                    
                    # Normalizzazione dati
                    events = [t_stream] if isinstance(t_stream, dict) and 'id' in t_stream else list(t_stream.values()) if isinstance(t_stream, dict) else t_stream

                    for e in events:
                        e_id = e.get('id')
                        val = e.get('value')
                        ts = e.get('timestamp')

                        # 1. Aggiornamento UI e Grafici
                        if e_id in sensor_updaters:
                            sensor_updaters[e_id](f"{val} {e.get('unit', '')}")
                            if e_id == 'greenhouse_temperature': update_temp_chart(val, ts)
                            elif e_id == 'entrance_humidity': update_hum_chart(val, ts)

                        topic = f"mars/telemetry/{e_id}"
                        if topic in tel_updaters:
                            tel_updaters[topic](extract_telemetry_data(e))

                        # 2. 🧠 IL MOTORE REGOLE (Frontend Side)
                        current_rules = get_rules()
                        if current_rules:
                            for rule in current_rules:
                                if rule.get('sensor_name') == e_id:
                                    v_float = float(val)
                                    target = float(rule.get('value'))
                                    op = rule.get('operator')
                                    
                                    # Verifica condizione
                                    triggered = False
                                    if op == '>': triggered = v_float > target
                                    elif op == '<': triggered = v_float < target
                                    elif op == '=': triggered = v_float == target

                                    if triggered:
                                        act_id = rule.get('actuator_name')
                                        target_state = rule.get('state') # ON / OFF

                                        if act_id in act_updaters:
                                            # Leggiamo lo stato attuale della UI per evitare loop di POST
                                            is_on = act_updaters[act_id].switch.value
                                            current_ui_str = 'ON' if is_on else 'OFF'

                                            if current_ui_str != target_state:
                                                print(f"⚡ [AUTOMAZIONE] Scatto: {e_id}({v_float}) {op} {target} -> {act_id}:{target_state}", flush=True)
                                                
                                                # AZIONE A: POST al Backend (Comando Reale)
                                                #set_actuator_state(act_id, target_state)
                                                
                                                # AZIONE B: Aggiorna lo switch (Grafica + Popup)
                                                act_updaters[act_id].update_from_rule(target_state)
                        
                        # 3. FEEDBACK: Se arriva un cambio stato da ActiveMQ, aggiorna lo switch
                        if e_id in act_updaters:
                            act_updaters[e_id].update_from_rule(str(val))

                except Exception as ex:
                    print(f"❌ Errore ws_listener: {ex}", flush=True)
                    await asyncio.sleep(1)

        # Avvio task asincrono
        bg_task = asyncio.create_task(ws_listener())
        ui.context.client.on_disconnect(lambda: bg_task.cancel())