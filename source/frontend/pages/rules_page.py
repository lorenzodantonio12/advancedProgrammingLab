from nicegui import ui
from services.api import get_rules, add_rule, delete_rule, edit_rule

# Sensor and actuator icons/names mapping
REST_SENSOR_ICONS = {
    'greenhouse_temperature': ('thermostat', 'Greenhouse Temp', 'red'),
    'entrance_humidity': ('water_drop', 'Entrance Humidity', 'blue'),
    'co2_hall': ('co2', 'Corridor CO2', 'green'),
    'corridor_pressure': ('compress', 'Corridor Pressure', 'purple'),
    'hydroponic_ph': ('science', 'Hydroponic pH', 'teal'),
    'air_quality_voc': ('air', 'Air Quality VOC', 'orange'),
    'air_quality_pm25': ('blur_on', 'Air Quality PM2.5', 'gray'),
    'water_tank_level': ('waves', 'Water Tank Level', 'cyan'),
}

TELEMETRY_ICONS = {
    'solar_array': ('solar_power', 'Solar Panels', 'orange'),
    'radiation': ('radar', 'Radiation', 'purple'),
    'life_support': ('favorite', 'Life Support', 'green'),
    'thermal_loop': ('severe_cold', 'Thermal Loop', 'blue'),
    'power_bus': ('electrical_services', 'Power Bus', 'yellow'),
    'power_consumption': ('electric_bolt', 'Power Consumption', 'red'),
    'airlock': ('meeting_room', 'Airlock', 'gray'),
}

SENSOR_ICONS = {**REST_SENSOR_ICONS, **TELEMETRY_ICONS}

ACTUATOR_ICONS = {
    'cooling_fan': ('ac_unit', 'Cooling Fan', 'blue'),
    'entrance_humidifier': ('water_drop', 'Humidifier', 'cyan'),
    'hall_ventilation': ('air', 'Ventilation', 'teal'),
    'habitat_heater': ('fireplace', 'Heater', 'orange'),
}

OPERATOR_ICONS = {
    '>': ('arrow_upward', 'Greater than'),
    '<': ('arrow_downward', 'Less than'),
    '>=': ('trending_up', 'Greater or equal'),
    '<=': ('trending_down', 'Less or equal'),
    '=': ('equal', 'Equal to'),
}


REST_SENSOR_METRICS = {
    'greenhouse_temperature': ['temperature_c'],
    'entrance_humidity': ['humidity_pct'],
    'co2_hall': ['co2_ppm'],
    'corridor_pressure': ['pressure_kpa'],
    'hydroponic_ph': ['ph'], 
    'air_quality_voc': ['voc_ppb', 'co2e_ppm'],
    'air_quality_pm25': ['pm1', 'pm25', 'pm10'],
    'water_tank_level': ['level_pct', 'level_liters'],
}

TELEMETRY_METRICS = {
    'solar_array': ['power_kw', 'voltage_v', 'current_a', 'cumulative_kwh'],
    'power_bus': ['power_kw', 'voltage_v', 'current_a', 'cumulative_kwh'],
    'power_consumption': ['power_kw', 'voltage_v', 'current_a', 'cumulative_kwh'],
    'radiation': ['radiation_uSv_h'],
    'life_support': ['oxygen_percent'],
    'thermal_loop': ['temperature', 'flow'],
    'airlock': ['cycles_per_hour'],
}

SENSOR_METRICS = {**REST_SENSOR_METRICS, **TELEMETRY_METRICS}

def setup_rules_page(navigation_bar_func):
    
    @ui.page('/rules')
    def rules_page():
        navigation_bar_func()
        ui.label('Automation Engine').classes('text-3xl font-bold w-full text-center mt-8 mb-8 text-gray-800')
        
        sens_list = list(SENSOR_ICONS.keys())
        act_list = list(ACTUATOR_ICONS.keys())

        # --- CREATE NEW RULE CARD ---
        with ui.card().classes('w-4/5 mx-auto p-8 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg border-2 border-blue-200 rounded-xl'):
            ui.label('Create Automation Rule').classes('text-2xl font-bold mb-6 text-blue-900')
            
            with ui.row().classes('w-full items-end gap-6 flex-wrap'):
                # Sensor section
                with ui.column().classes('gap-2'):
                    ui.icon('sensors').classes('text-3xl text-blue-600')
                    s = ui.select(sens_list, label='Sensor', value=sens_list[0] if sens_list else None).classes('w-56')

                #metric section
                with ui.column().classes('gap-2'):
                    ui.icon('straighten').classes('text-3xl text-indigo-600')
                    # All'inizio mostra le metriche del primo sensore selezionato
                    m_select = ui.select(SENSOR_METRICS[s.value], label='Metric', value=SENSOR_METRICS[s.value][0]).classes('w-40')

                #metriche a seconda del sensore
                def update_metrics(e):
                    # e.value è il nuovo sensore scelto
                    nuove_metriche = SENSOR_METRICS[e.value]
                    m_select.options = nuove_metriche
                    m_select.value = nuove_metriche[0] # Seleziona in automatico la prima
                    m_select.update()
                
                s.on_value_change(update_metrics)
                
                # Operator section
                with ui.column().classes('gap-2'):
                    ui.icon('compare').classes('text-3xl text-purple-600')
                    o = ui.select(list(OPERATOR_ICONS.keys()), label='Operator', value='>' if OPERATOR_ICONS else None).classes('w-32')
                
                # Value section
                with ui.column().classes('gap-2'):
                    ui.icon('input').classes('text-3xl text-green-600')
                    v = ui.input(label='Value', placeholder='e.g., 25').classes('w-32')
                
                # Arrow
                ui.label('→').classes('text-4xl font-bold text-gray-400')
                
                # Actuator section
                with ui.column().classes('gap-2'):
                    ui.icon('outlet').classes('text-3xl text-orange-600')
                    a = ui.select(act_list, label='Actuator', value=act_list[0] if act_list else None).classes('w-56')
                
                # Action section
                with ui.column().classes('gap-2'):
                    ui.icon('power_settings_new').classes('text-3xl text-red-600')
                    av = ui.select(['ON', 'OFF'], label='Action', value='ON').classes('w-32')
                
                # Save button
                def save_rule():
                    if all([s.value, m_select.value, o.value, v.value, a.value, av.value]):

                        success = add_rule(s.value, m_select.value, o.value, v.value, a.value, av.value)

                        if success:
                            ui.notify('✓ Rule created!', position='top', type='positive')
                            s.set_value(sens_list[0] if sens_list else None)
                            o.set_value('>')
                            v.set_value('')
                            a.set_value(act_list[0] if act_list else None)
                            av.set_value('ON')
                            table.refresh()
                        else:
                            ui.notify('⚠ Conflict detected! This rule overlaps with an existing one.', position='top', type='negative', timeout=5000)
                    else:
                        ui.notify('⚠ Fill all fields!', position='top', type='warning')
                
                ui.button('Create Rule', on_click=save_rule, icon='add').classes('h-12 px-8 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold shadow-lg hover:shadow-xl')

        # --- ACTIVE RULES LIST ---
        ui.label('Active Rules').classes('text-2xl font-bold w-full text-center mt-12 mb-6 text-gray-800')
        
        @ui.refreshable
        def table():
            rules = get_rules()
            if not rules:
                with ui.column().classes('w-full items-center justify-center mt-8'):
                    ui.icon('info').classes('text-6xl text-gray-300')
                    ui.label('No active rules yet').classes('text-lg text-gray-500 mt-4')
                return
            
            with ui.column().classes('w-4/5 mx-auto gap-4'):
                for r in rules:
                    # Legge i dati usando le chiavi del backend (sensor_name, actuator_name, state)
                    sen_key = r.get('sensor_name', '')
                    act_key = r.get('actuator_name', '')
                    metric_key = r.get('metric', '') 
                    
                    sen_icon, sen_name, sen_col = SENSOR_ICONS.get(sen_key, ('sensors', sen_key, 'gray'))
                    act_icon, act_name, act_col = ACTUATOR_ICONS.get(act_key, ('outlet', act_key, 'gray'))
                    op_icon, op_desc = OPERATOR_ICONS.get(r.get('operator', ''), ('help', r.get('operator', '')))
                    
                    with ui.card().classes('w-full p-5 bg-white shadow-md border-l-4 border-blue-500 hover:shadow-lg transition'):
                        with ui.row().classes('w-full items-center justify-between gap-6 flex-wrap'):
                            # Sensor and metric
                            with ui.row().classes('items-center gap-2'):
                                ui.icon(sen_icon).classes(f'text-2xl text-{sen_col}-600')
                                with ui.column().classes('gap-0'):
                                    ui.label('IF').classes('text-xs font-bold text-gray-500 uppercase')
                                    ui.label(sen_name).classes('font-semibold text-gray-800')
                                    ui.label(metric_key).classes('text-xs text-blue-500 font-mono') 
                            
                            # Operator and value
                            with ui.row().classes('items-center gap-2'):
                                ui.icon(op_icon).classes(f'text-xl text-purple-600')
                                ui.label(r.get('operator', '')).classes('font-bold text-lg text-purple-700')
                                ui.label(str(r.get('value', ''))).classes('font-mono bg-gray-100 px-3 py-1 rounded text-gray-800')
                            
                            # Arrow
                            ui.label('→').classes('text-2xl font-bold text-gray-400')
                            
                            # Actuator
                            with ui.row().classes('items-center gap-2'):
                                ui.icon(act_icon).classes(f'text-2xl text-{act_col}-600')
                                with ui.column().classes('gap-1'):
                                    ui.label('THEN').classes('text-xs font-bold text-gray-500 uppercase')
                                    ui.label(act_name).classes('font-semibold text-gray-800')
                            
                            # Action
                            action_state = r.get('state', 'OFF')
                            action_color = 'green' if action_state == 'ON' else 'red'
                            with ui.row().classes(f'items-center gap-2 px-3 py-2 rounded-lg bg-{action_color}-100'):
                                ui.icon('power_settings_new').classes(f'text-xl text-{action_color}-600')
                                ui.label(action_state).classes(f'font-bold text-{action_color}-700')
                            
                            # Delete and update button

                            with ui.row().classes('gap-2'):
                                # Funzione per aprire il popup di modifica
                                def open_edit(rule=r):
                                    with ui.dialog() as dialog, ui.card().classes('p-6'):
                                        ui.label('Edit Rule').classes('text-xl font-bold mb-4')
                                        
                                        # Campi modificabili
                                        edit_op = ui.select(list(OPERATOR_ICONS.keys()), label='Operator', value=rule.get('operator')).classes('w-full mb-2')
                                        edit_val = ui.input(label='Value', value=str(rule.get('value'))).classes('w-full mb-2')
                                        edit_act = ui.select(list(ACTUATOR_ICONS.keys()), label='Actuator', value=rule.get('actuator_name')).classes('w-full mb-2')
                                        edit_state = ui.select(['ON', 'OFF'], label='Action', value=rule.get('state')).classes('w-full mb-4')
                                        
                                        def save_changes():
                                            update_data = {
                                                "operator": edit_op.value,
                                                "value": float(edit_val.value),
                                                "actuator_name": edit_act.value,
                                                "state": edit_state.value
                                            }

                                            success, message = edit_rule(rule.get('id_rule'), update_data)

                                            if success:
                                                ui.notify('✓ Rule updated', type='positive')
                                                dialog.close()
                                                table.refresh()
                                            else:
                                                if message == "conflict":
                                                    ui.notify('⚠ Conflict detected! This rule overlaps with an existing one.', position='top', type='negative', timeout=5000)
                                                elif message == "not_found":
                                                    ui.notify('⚠ Rule not found in database.', position='top', type='warning')
                                                else:
                                                    ui.notify('⚠ Error updating rule. Check your data.', position='top', type='negative')
                                                
                                        with ui.row().classes('w-full justify-end gap-2'):
                                            ui.button('Cancel', on_click=dialog.close).props('flat')
                                            ui.button('Save', on_click=save_changes).classes('bg-blue-600 text-white')
                                            
                                    dialog.open()

                                # Bottone Modifica
                                ui.button(icon='edit', on_click=open_edit).props('flat round').classes('text-blue-600 hover:bg-blue-50')
                                
                                # Bottone Elimina 
                                def delete_rule_handler(rule_id=r.get('id_rule')):
                                    delete_rule(rule_id)
                                    ui.notify('✓ Rule deleted', position='top', type='info')
                                    table.refresh()
                                
                                ui.button(icon='delete_outline', on_click=delete_rule_handler).props('flat round').classes('text-red-600 hover:bg-red-50')

        
        table()