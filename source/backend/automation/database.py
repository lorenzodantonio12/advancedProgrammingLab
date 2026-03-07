import sqlite3

def create_database():
    conn = sqlite3.connect("mars_rules.db")

    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS rules (
                id_rule INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_name TEXT NOT NULL,
                operator TEXT NOT NULL,
                value REAL NOT NULL,
                metric TEXT NOT NULL,
                actuator_name TEXT NOT NULL,
                state TEXT)""")

    conn.commit()