import asyncio
from nicegui import ui

from components.sensor_widget import SensorWidget, MultiSensorWidget 
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
from utils import extract_telemetry_data


def setup_dashboard_page(navigation_bar_func):
    @ui.page('/')
    async def dashboard_page():
        navigation_bar_func()
        
        # --- 1. SENSORI ---
        # 🟢 TITOLO ANIMATO: Radar pulsante
        with ui.row().classes('w-full justify-center items-center gap-2 mt-6'):
            ui.image('/assets/multiple-sensor.gif').classes('w-16 h-16')
            ui.label('Environmental Sensors').classes('text-2xl font-bold text-gray-800')
            
        sensor_updaters = {}
        multi_updaters = {}
        
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            sensor_updaters['greenhouse_temperature'] = SensorWidget('Greenhouse Temp', 'thermostat', 'red')
            sensor_updaters['entrance_humidity'] = SensorWidget('Entrance Humidity', 'water_drop', 'blue')
            sensor_updaters['co2_hall'] = SensorWidget('Corridor CO2', 'co2', 'green')
            sensor_updaters['corridor_pressure'] = SensorWidget('Corridor Pressure', 'compress', 'purple')
            sensor_updaters['hydroponic_ph'] = SensorWidget('Hydroponic pH', 'science', 'teal')

            multi_updaters['air_quality_voc'] = MultiSensorWidget('Air Quality VOC', 'air', 'orange')
            multi_updaters['air_quality_pm25'] = MultiSensorWidget('Particulate (PM)', 'blur_on', 'grey')
            multi_updaters['water_tank_level'] = MultiSensorWidget('Water Tank', 'waves', 'cyan')

        # --- 2. GRAFICI ---
        # 🟢 TITOLO ANIMATO: Grafico che rimbalza leggermente
        with ui.row().classes('w-full justify-center items-center gap-2 mt-8'):
            ui.image('/assets/wave-graph.gif').classes('w-16 h-16')
            ui.label('Data Graphs').classes('text-2xl font-bold text-gray-800')
            
        with ui.row().classes('w-full gap-4 p-4 justify-center flex-wrap lg:flex-nowrap'):
            update_temp_chart = SingleChartFactory('Temperature Graph', 'Temp', '#ef4444', '°C')
            update_hum_chart = SingleChartFactory('Humidity Graph', 'Humidity', '#3b82f6', '%')

        # --- 3. ATTUATORI ---
        # 🟢 TITOLO ANIMATO: Ingranaggio che gira
        with ui.row().classes('w-full justify-center items-center gap-2 mt-8'):
            ui.image('/assets/switch.gif').classes('w-16 h-16')
            ui.label('Actuators Control').classes('text-2xl font-bold text-gray-800')
            
        act_states = get_initial_actuators_state() or {}
        act_updaters = {}
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            act_updaters['cooling_fan'] = ActuatorWidget('Cooling Fan', 'ac_unit', 'blue', 'cooling_fan', act_states.get('cooling_fan', 'OFF'))
            act_updaters['entrance_humidifier'] = ActuatorWidget('Humidifier', 'water_drop', 'cyan', 'entrance_humidifier', act_states.get('entrance_humidifier', 'OFF'))
            act_updaters['hall_ventilation'] = ActuatorWidget('Ventilation', 'air', 'teal', 'hall_ventilation', act_states.get('hall_ventilation', 'OFF'))
            act_updaters['habitat_heater'] = ActuatorWidget('Heater', 'fireplace', 'orange', 'habitat_heater', act_states.get('habitat_heater', 'OFF'))

        # --- 4. TELEMETRIA ---
        # 🟢 TITOLO ANIMATO: Antenna di trasmissione pulsante
        with ui.row().classes('w-full justify-center items-center gap-2 mt-8'):
            ui.image('/assets/space-station.gif').classes('w-16 h-16')
            ui.label('Live Telemetry').classes('text-2xl font-bold text-gray-800')
            
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
                tel_updaters[eid] = TelemetryWidget(name, icon, col)
        page_client = ui.context.client
        # --- 🚀 WEBSOCKET LISTENER ---
        async def ws_listener():
            history = get_latest_sensor_data()
            if history:
                for h_ev in history:
                    h_id = h_ev.get('id', '')
                    h_metric = h_ev.get('metric', h_id)
                    h_val, h_ts = h_ev.get('value'), h_ev.get('timestamp')
                    
                    if h_metric == 'greenhouse_temperature' or h_id == 'greenhouse_temperature':
                        update_temp_chart(h_val, h_ts)
                    elif h_metric == 'entrance_humidity' or h_id == 'entrance_humidity':
                        update_hum_chart(h_val, h_ts)

            while True:
                try:
                    t_stream = await get_next_push_event()
                    if not t_stream: continue
                    
                    events = [t_stream] if isinstance(t_stream, dict) and 'id' in t_stream else list(t_stream.values()) if isinstance(t_stream, dict) else t_stream

                    for e in events:
                        e_id = e.get('id', '')
                        metric = e.get('metric', e_id) 
                        val = e.get('value')
                        ts = e.get('timestamp')
                        unit = e.get('unit', '')
                        v_str = f"{val} {unit}".strip()

                        # A & B. Aggiornamento Card Sensori
                        if metric in sensor_updaters:
                            sensor_updaters[metric](v_str)
                        elif e_id in sensor_updaters:
                            sensor_updaters[e_id](v_str)

                        if e_id in multi_updaters:
                            multi_updaters[e_id](metric, v_str)

                        # C. Grafici
                        if metric == 'greenhouse_temperature' or e_id == 'greenhouse_temperature':
                            update_temp_chart(val, ts)
                        elif metric == 'entrance_humidity' or e_id == 'entrance_humidity':
                            update_hum_chart(val, ts)

                        # D. Telemetria
                        if e_id in tel_updaters:
                            new_data = extract_telemetry_data(e)
                            tel_updaters[e_id](new_data)

                        # --- MOTORE REGOLE ---
                        current_rules = get_rules()
                        if current_rules:
                            for rule in current_rules:
                                if rule.get('sensor_name') in [e_id, metric]:
                                    try:
                                        v_float = float(val)
                                        target = float(rule.get('value', 0))
                                    except (ValueError, TypeError):
                                        continue 
                                        
                                    op = rule.get('operator')
                                    
                                    triggered = False
                                    if op == '>': triggered = v_float > target
                                    elif op == '<': triggered = v_float < target
                                    elif op == '=': triggered = v_float == target
                                    elif op == '>=': triggered = v_float >= target
                                    elif op == '<=': triggered = v_float <= target

                                    if triggered:
                                        act_id = rule.get('actuator_name')
                                        target_state = rule.get('state')

                                        if act_id in act_updaters:
                                            is_on = act_updaters[act_id].switch.value
                                            current_ui_str = 'ON' if is_on else 'OFF'

                                            if current_ui_str != target_state:
                                                print(f"⚡ [AUTOMAZIONE] Scatto: {metric}({v_float}) {op} {target} -> {act_id}:{target_state}", flush=True)
                                                set_actuator_state(act_id, target_state)
                                                
                                                # 🟢 FIX 2: Usiamo il 'page_client' che abbiamo salvato fuori dal loop
                                                with page_client:
                                                    act_updaters[act_id].update_from_rule(target_state)
                                                    #ui.notify(f"⚡ Automazione: {act_id.replace('_', ' ').title()} -> {target_state}", color='warning', icon='bolt', position='top')
                        # Feedback Attuatori
                        if e_id in act_updaters:
                            act_updaters[e_id].update_from_rule(str(val))

                except Exception as ex:
                    print(f"❌ Errore ws_listener: {ex}", flush=True)
                    await asyncio.sleep(1)

        bg_task = asyncio.create_task(ws_listener())
        ui.context.client.on_disconnect(lambda: bg_task.cancel())