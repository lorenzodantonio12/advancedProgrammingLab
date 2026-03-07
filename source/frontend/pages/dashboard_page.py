import asyncio
from nicegui import ui

from components.sensor_widget import SensorWidget
from components.actuator_toggle import ActuatorWidget
from components.telemetry_widget import TelemetryWidget
from components.sensor_chart import SingleChartFactory
from services.api import (
    get_latest_sensor_data, get_initial_actuators_state, 
    get_telemetry_stream_mock, get_rules, get_next_push_event
)


def extract_telemetry_data(t_data):
    ui_data = {}
    if "power_kw" in t_data:
        ui_data["Power"] = f"{t_data['power_kw']} kW"
        ui_data["Voltage"] = f"{t_data['voltage_v']} V"
    elif "measurements" in t_data:
        for m in t_data["measurements"]:
            ui_data[m['metric'].replace('_', ' ').title()] = f"{m['value']} {m['unit']}"
    elif "temperature_c" in t_data:
        ui_data["Temperature"] = f"{t_data['temperature_c']} °C"
        ui_data["Flow"] = f"{t_data['flow_l_min']} L/min"
    elif "last_state" in t_data:
        ui_data["Status"] = t_data["last_state"]
        ui_data["Cycles/h"] = t_data["cycles_per_hour"]
    return ui_data


def setup_dashboard_page(navigation_bar_func):
    @ui.page('/')
    async def dashboard_page():
        navigation_bar_func()
        
        ui.label('Environmental Sensors').classes('text-2xl font-bold w-full text-center mt-6')
        sensor_updaters = {}
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            sensor_updaters['greenhouse_temperature'] = SensorWidget('Greenhouse Temperature', 'thermostat', 'red')
            sensor_updaters['entrance_humidity'] = SensorWidget('Entrance Humidity', 'water_drop', 'blue')
            sensor_updaters['co2_hall'] = SensorWidget('Corridor CO2', 'co2', 'green')
            sensor_updaters['corridor_pressure'] = SensorWidget('Corridor Pressure', 'compress', 'purple')
            sensor_updaters['hydroponic_ph'] = SensorWidget('Hydroponic pH', 'science', 'teal')
            sensor_updaters['air_quality_voc'] = SensorWidget('Air Quality VOC', 'air', 'orange')
            sensor_updaters['air_quality_pm25'] = SensorWidget('Air Quality PM2.5', 'blur_on', 'grey')
            sensor_updaters['water_tank_level'] = SensorWidget('Water Tank Level', 'waves', 'cyan')

        with ui.row().classes('w-full gap-4 p-4 justify-center flex-wrap lg:flex-nowrap'):
            update_temp_chart = SingleChartFactory('Temperature Chart', 'Temp', '#ef4444', '°C')
            update_hum_chart = SingleChartFactory('Humidity Chart', 'Humidity', '#3b82f6', '%')

        ui.label('Actuators Control').classes('text-2xl font-bold w-full text-center mt-8')
        act_states = get_initial_actuators_state()
        act_updaters = {}
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            act_updaters['cooling_fan'] = ActuatorWidget('Cooling Fan', 'ac_unit', 'blue', 'cooling_fan', act_states.get('cooling_fan'))
            act_updaters['entrance_humidifier'] = ActuatorWidget('Entrance Humidifier', 'water_drop', 'cyan', 'entrance_humidifier', act_states.get('entrance_humidifier'))
            act_updaters['hall_ventilation'] = ActuatorWidget('Corridor Ventilation', 'air', 'teal', 'hall_ventilation', act_states.get('hall_ventilation'))
            act_updaters['habitat_heater'] = ActuatorWidget('Habitat Heater', 'fireplace', 'orange', 'habitat_heater', act_states.get('habitat_heater'))

        ui.label('Live Telemetry').classes('text-2xl font-bold w-full text-center mt-8')
        tel_updaters = {}
        tel_defs = {
            'mars/telemetry/solar_array': ('Solar Panels', 'solar_power', 'orange'),
            'mars/telemetry/power_bus': ('Power Bus', 'electrical_services', 'yellow'),
            'mars/telemetry/power_consumption': ('Power Consumption', 'electric_bolt', 'red'),
            'mars/telemetry/radiation': ('Radiation', 'radar', 'purple'),
            'mars/telemetry/life_support': ('Life Support', 'favorite', 'green'),
            'mars/telemetry/thermal_loop': ('Thermal Loop', 'severe_cold', 'blue'),
            'mars/telemetry/airlock': ('Airlock', 'meeting_room', 'grey'),
        }
        with ui.row().classes('w-full justify-center gap-4 p-4 flex-wrap'):
            for topic, (name, icon, col) in tel_defs.items():
                tel_updaters[topic] = TelemetryWidget(name, icon, col)

        def update_rest_data():
            raw = get_latest_sensor_data()
            grouped = {}
            for e in raw:
                sid = e['id']
                if sid not in grouped: grouped[sid] = []
                grouped[sid].append(e)
                if sid in sensor_updaters:
                    sensor_updaters[sid](f"{e['value']} {e['unit'] or ''}")

            t = next((e['value'] for e in raw if e['id'] == 'greenhouse_temperature'), None)
            h = next((e['value'] for e in raw if e['id'] == 'entrance_humidity'), None)
            update_temp_chart(t)
            update_hum_chart(h)

            for rule in get_rules():
                if rule['sensor'] in grouped:
                    val = float(grouped[rule['sensor']][0]['value'])
                    target = float(rule['value'])
                    trigger = False
                    op = rule['operator']
                    if op == '>': trigger = val > target
                    elif op == '<': trigger = val < target
                    elif op == '>=': trigger = val >= target
                    elif op == '<=': trigger = val <= target
                    elif op == '=': trigger = val == target
                    if trigger and rule['actuator'] in act_updaters:
                        act_updaters[rule['actuator']](rule['action'])

            t_stream = get_telemetry_stream_mock()
            for topic, data in t_stream.items():
                if topic in tel_updaters:
                    tel_updaters[topic](extract_telemetry_data(data))

        async def ws_listener():
            while True:
                try:
                    t_stream = await get_next_push_event()
                    for topic, data in t_stream.items():
                        if topic in tel_updaters:
                            tel_updaters[topic](extract_telemetry_data(data))
                except Exception as e:
                    print(f"WebSocket error: {e}")
                    await asyncio.sleep(1)

        ui.timer(5.0, update_rest_data)
        asyncio.create_task(ws_listener())
