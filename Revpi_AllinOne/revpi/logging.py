# ============================== # IMPORT LIBRARY # ==============================
import sqlite3
import csv
from datetime import datetime
import os
import logging

logger = logging.getLogger("revpi/logger")

# =============================== # PATH # ===============================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "data_logging")
DB_FILE = os.path.join(LOG_DIR, "data.db")

# =============================== # FIELD DEFINITIONS # ===============================
MEASUREMENT_FIELDS = [
    "timestamp", "ANALOG", "RTD", "TEMP", "HUM",
    "LED1", "LED2", "LED3", "LED4", "LED6", "LED7",
    "BUZZ1", "BUZZ2"
]

EVENT_FIELDS = ["timestamp", "actuator", "status"]

# =============================== # INIT LOG FOLDER # ===============================
def init_log_folder():
    os.makedirs(LOG_DIR, exist_ok=True)

# =============================== # INIT DATABASE # ===============================
def init_db():
    init_log_folder()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            timestamp TEXT,
            ANALOG REAL, RTD REAL, TEMP REAL, HUM REAL,
            LED1 INTEGER, LED2 INTEGER, LED3 INTEGER,
            LED4 INTEGER, LED6 INTEGER, LED7 INTEGER,
            BUZZ1 INTEGER, BUZZ2 INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS event (
            timestamp TEXT, actuator TEXT, status TEXT
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Logger database initialized")

# =============================== # INIT CSV # ===============================
def init_csv():
    init_log_folder()
    _write_header("measurements.csv", MEASUREMENT_FIELDS)
    _write_header("event.csv", EVENT_FIELDS)

def _write_header(filename, fields):
    path = os.path.join(LOG_DIR, filename)
    if not os.path.isfile(path):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

# =============================== # LOG MEASUREMENTS # ===============================
def measurements(data: dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"timestamp": timestamp, **{k: data.get(k) for k in MEASUREMENT_FIELDS[1:]}}
    _insert_db("measurements", [row[k] for k in MEASUREMENT_FIELDS])
    _insert_csv("measurements.csv", MEASUREMENT_FIELDS, row)

# =============================== # LOG EVENT # ===============================
def event(actuator: str, status: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"timestamp": timestamp, "actuator": actuator, "status": status}
    _insert_db("event", list(row.values()))
    _insert_csv("event.csv", EVENT_FIELDS, row)

# =============================== # DB INSERT # ===============================
def _insert_db(table, values):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        placeholders = ",".join(["?"] * len(values))
        c.execute(f"INSERT INTO {table} VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.exception("DB insert error: %s", e)

# =============================== # CSV INSERT # ===============================
def _insert_csv(filename, fields, values):
    path = os.path.join(LOG_DIR, filename)
    try:
        with open(path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writerow(values)
    except Exception as e:
        logger.exception("CSV insert error: %s", e)
