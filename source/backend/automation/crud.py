from models import AutomationRule, StandardFormat
from check_interval import check_overlap
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


db = str(BASE_DIR / "data" / "mars_rules.db")

def get_rules():
    try:
        with sqlite3.connect(db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""SELECT * from rules""")
            results = cursor.fetchall()

            return [AutomationRule(**dict(row)) for row in results]
        
    except sqlite3.Error as e:
        print(f"Errore DB in get_rules: {e}")
        return []   

def create_rule(rule: AutomationRule):
    try:

        with sqlite3.connect(db) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM rules 
                WHERE sensor_name = ? AND metric = ? AND actuator_name = ?
            """, (rule.sensor_name, rule.metric, rule.actuator_name))
            
            
            existing_rules = cursor.fetchall()

            for existing in existing_rules:
                if existing['state'] != rule.state:
                    
                    is_overlapping = check_overlap(
                        rule.operator, rule.value, 
                        existing['operator'], existing['value']
                    )
                    
                    if is_overlapping:
                        return False

            params = (rule.sensor_name, rule.operator, rule.value, rule.metric, rule.actuator_name, rule.state)

            cursor.execute("""INSERT INTO rules (sensor_name, operator, value, metric, actuator_name, state) VALUES (?, ?, ?, ?, ?, ?)""", params)

            conn.commit()

            return cursor.lastrowid
        
    except sqlite3.Error as e:
        print(f"Errore DB in create_rule: {e}")
        return None
    
def update_rule(id_rule: int, data: dict):

    if not data:
        return False
    
    columns = {"operator", "value", "metric", "actuator_name", "state"}

    valid_data = {k: v for k, v in data.items() if k in columns}

    if not valid_data:
        return False, "invalid data"
    
    try:

        with sqlite3.connect(db) as conn:
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()

            cursor.execute("""SELECT * FROM rules WHERE id_rule = ?""", (id_rule,))
            current_rule = cursor.fetchone()

            if not current_rule:
                return False, "not found"
            
            proposed_rule = dict(current_rule)
            proposed_rule.update(valid_data)

            p_sensor = proposed_rule.get('sensor_name')
            p_metric = proposed_rule.get('metric')
            p_actuator = proposed_rule.get('actuator_name')
            p_state = proposed_rule.get('state')
            p_operator = proposed_rule.get('operator')
            p_value = proposed_rule.get('value')

            params = (p_sensor, p_metric, p_actuator, id_rule)

            cursor.execute("""SELECT * FROM rules
                        WHERE sensor_name = ? AND metric = ? AND actuator_name = ? AND id_rule != ?""", params)

            existing_rules = cursor.fetchall()

            for existing in existing_rules:
                if existing['state'] != p_state:
                    
                    is_overlapping = check_overlap(
                        p_operator, p_value, 
                        existing['operator'], existing['value']
                    )
                    
                    if is_overlapping:
                        return False, "conflict"
        
        string = []
        values = []

        for key, val in valid_data.items():
            string.append(f"{key} = ?")
            values.append(val)

        values.append(id_rule)

        s = ",".join(string)

        query = f"UPDATE rules SET {s} WHERE id_rule = ?"

        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()

            params = tuple(values)

            cursor.execute(query, params)

            conn.commit()

            if cursor.rowcount > 0:
                return True, "success"
            
        return False, "error"
    except sqlite3.Error as e:
        print(f"Errore DB in update_rule: {e}")
        return False, "error"
    
def delete_rule(id_rule: int):
    try: 
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()

            cursor.execute("""DELETE FROM rules WHERE id_rule=?""", (id_rule,))

            conn.commit()
    except sqlite3.Error as e:
        print(f"Errore DB in delete_rule: {e}")
