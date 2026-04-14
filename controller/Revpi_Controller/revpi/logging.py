# ============================== # IMPORT LIBRARY # ==============================
import sqlite3
import csv
import json
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
    "timestamp",
    "epoch_ms",
    "command_id",
    "ANALOG", "RTD", "TEMP", "HUM",
    "LED1", "LED2", "LED3", "LED4", "LED6", "LED7",
    "BUZZ1", "BUZZ2",
    "bytes_sent"
]

EVENT_FIELDS = [
    "timestamp",
    "epoch_ms",
    "command_id",
    "actuator",
    "status",
    "exec_time_ms",
    "success"
]

ACK_FIELDS = [
    "timestamp",
    "epoch_ms",
    "command_id",
    "source",
    "status",
    "latency_ms"
]

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
            timestamp TEXT, epoch_ms REAL, command_id TEXT, ANALOG REAL, RTD REAL,
            TEMP REAL, HUM REAL, LED1 INTEGER, LED2 INTEGER, LED3 INTEGER, LED4 INTEGER,
            LED6 INTEGER, LED7 INTEGER, BUZZ1 INTEGER, BUZZ2 INTEGER, bytes_sent INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS event (
            timestamp TEXT, epoch_ms REAL, command_id TEXT, actuator TEXT, status TEXT,
            exec_time_ms REAL, success INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS ack (
            timestamp TEXT, epoch_ms REAL, command_id TEXT, source TEXT,
            status TEXT, latency_ms REAL
        )
    """)

    conn.commit()
    conn.close()
    logger.info("Logger database initialized")

# ===============================# INIT CSV # ===============================
def init_csv():
    init_log_folder()
    _write_header("measurements.csv", MEASUREMENT_FIELDS)
    _write_header("event.csv", EVENT_FIELDS)
    _write_header("ack.csv", ACK_FIELDS)

def _write_header(filename, fields):
    path = os.path.join(LOG_DIR, filename)
    if not os.path.isfile(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

# =============================== # LOG MEASUREMENTS # ===============================
def measurements(data: dict):
    now = datetime.now()

    row = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "epoch_ms": now.timestamp() * 1000,
        "command_id": data.get("command_id", ""),
        "ANALOG": data.get("ANALOG"),
        "RTD": data.get("RTD"),
        "TEMP": data.get("TEMP"),
        "HUM": data.get("HUM"),
        "LED1": int(bool(data.get("LED1", 0))),
        "LED2": int(bool(data.get("LED2", 0))),
        "LED3": int(bool(data.get("LED3", 0))),
        "LED4": int(bool(data.get("LED4", 0))),
        "LED6": int(bool(data.get("LED6", 0))),
        "LED7": int(bool(data.get("LED7", 0))),
        "BUZZ1": int(bool(data.get("BUZZ1", 0))),
        "BUZZ2": int(bool(data.get("BUZZ2", 0))),
        "bytes_sent": len(json.dumps(data).encode("utf-8"))
    }

    _insert_db("measurements", [row[k] for k in MEASUREMENT_FIELDS])
    _insert_csv("measurements.csv", MEASUREMENT_FIELDS, row)


# =============================== # LOG EVENT # ===============================
def event(
    command_id: str,
    actuator: str,
    status: str,
    exec_time_ms: float,
    success: bool = True
):
    now = datetime.now()

    row = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "epoch_ms": now.timestamp() * 1000,
        "command_id": command_id,
        "actuator": actuator,
        "status": status,
        "exec_time_ms": exec_time_ms,
        "success": int(success)
    }

    _insert_db("event", [row[k] for k in EVENT_FIELDS])
    _insert_csv("event.csv", EVENT_FIELDS, row)


# =============================== # LOG ACK # ===============================
def ack(
    command_id: str,
    source: str,
    status: str,
    latency_ms: float
):
    now = datetime.now()

    row = {
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "epoch_ms": now.timestamp() * 1000,
        "command_id": command_id,
        "source": source,
        "status": status,
        "latency_ms": latency_ms
    }

    _insert_db("ack", [row[k] for k in ACK_FIELDS])
    _insert_csv("ack.csv", ACK_FIELDS, row)


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
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writerow(values)
    except Exception as e:
        logger.exception("CSV insert error: %s", e)