import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent

DATA_DIR = DB_DIR / "data"

DATA_DIR.mkdir(parents = True, exist_ok = True)

db = str(DATA_DIR / "mars_rules.db")

def create_database():
    conn = sqlite3.connect(db)

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