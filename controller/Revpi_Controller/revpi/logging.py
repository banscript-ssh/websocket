# ============================== # IMPORT LIBRARY # ============================== #
import csv
import logging
import os
import sqlite3
from datetime import datetime

logger = logging.getLogger("revpi/logger")

# ============================== # PATH # ============================== #
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(BASE_DIR, "data_logging")
DB_FILE = os.path.join(LOG_DIR, "data.db")

# ============================== # FIELD DEFINITIONS # ============================== #
MEASUREMENT_FIELDS = [
    "timestamp",
    "MODE",
    "TEMP",
    "HUM",
    "RTD",
    "ANALOG",
]

INDICATOR_FIELDS = [
    "timestamp",
    "MODE",
    "LED1",
    "LED2",
    "LED3",
    "LED4",
    "LED5",
    "LED6",
    "LED7",
    "LED8",
    "BUZZ1",
    "BUZZ2",
    "BUZZ3",
    "RELAY_MOTOR",
    "RELAY_FAN",
    "RELAY_LAMP",
]

EVENT_FIELDS = [
    "timestamp",
    "command_id",
    "actuator",
    "status",
    "exec_time_ms",
    "success",
]

ACK_FIELDS = [
    "timestamp",
    "command_id",
    "source",
    "status",
    "latency_ms",
]

SCENARIO_FIELDS = [
    "timestamp",
    "controller",
    "scenario",
    "mode",
    "source",
    "status",
    "cycle_ms",

    # Digital Input
    "PB1",
    "PB2",
    "PB3",
    "PB4",
    "PB5",
    "PB6",
    "PB7",
    "PB8",
    "EM9",
    "SW10",
    "SW11",
    "SW12",
    "SW13",
    "SW14",

    # Sensor
    "TEMP",
    "HUM",
    "RTD",
    "ANALOG",

    # Digital Output
    "LED1",
    "LED2",
    "LED3",
    "LED4",
    "LED5",
    "LED6",
    "LED7",
    "LED8",

    "BUZZ1",
    "BUZZ2",
    "BUZZ3",

    "RELAY_MOTOR",
    "RELAY_FAN",
    "RELAY_LAMP",
]

# ============================== # INIT LOG FOLDER # ============================== #
def init_log_folder():
    os.makedirs(LOG_DIR, exist_ok=True)

# ============================== # INIT DATABASE # ============================== #
def init_db():

    init_log_folder()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS measurements(
            timestamp TEXT,
            MODE TEXT,
            TEMP REAL,
            HUM REAL,
            RTD REAL,
            ANALOG REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS indicator(
            timestamp TEXT,
            MODE TEXT,
            LED1 INTEGER,
            LED2 INTEGER,
            LED3 INTEGER,
            LED4 INTEGER,
            LED5 INTEGER,
            LED6 INTEGER,
            LED7 INTEGER,
            LED8 INTEGER,
            BUZZ1 INTEGER,
            BUZZ2 INTEGER,
            BUZZ3 INTEGER,
            RELAY_MOTOR INTEGER,
            RELAY_FAN INTEGER,
            RELAY_LAMP INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS event(
            timestamp TEXT,
            command_id TEXT,
            actuator TEXT,
            status TEXT,
            exec_time_ms REAL,
            success INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS ack(
            timestamp TEXT,
            command_id TEXT,
            source TEXT,
            status TEXT,
            latency_ms REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS scenario(

            timestamp TEXT,
            controller TEXT,
            scenario TEXT,
            mode TEXT,
            source TEXT,
            status TEXT,
            cycle_ms REAL,

            PB1 INTEGER,
            PB2 INTEGER,
            PB3 INTEGER,
            PB4 INTEGER,
            PB5 INTEGER,
            PB6 INTEGER,
            PB7 INTEGER,
            PB8 INTEGER,

            EM9 INTEGER,

            SW10 INTEGER,
            SW11 INTEGER,
            SW12 INTEGER,
            SW13 INTEGER,
            SW14 INTEGER,

            TEMP REAL,
            HUM REAL,
            RTD REAL,
            ANALOG REAL,

            LED1 INTEGER,
            LED2 INTEGER,
            LED3 INTEGER,
            LED4 INTEGER,
            LED5 INTEGER,
            LED6 INTEGER,
            LED7 INTEGER,
            LED8 INTEGER,

            BUZZ1 INTEGER,
            BUZZ2 INTEGER,
            BUZZ3 INTEGER,

            RELAY_MOTOR INTEGER,
            RELAY_FAN INTEGER,
            RELAY_LAMP INTEGER

        )
    """)

    conn.commit()
    conn.close()

    logger.info("Logger initialized")

# ============================== # INIT CSV # ============================== #
def init_csv():

    init_log_folder()

    _write_header("measurements.csv", MEASUREMENT_FIELDS)
    _write_header("indicator.csv", INDICATOR_FIELDS)
    _write_header("event.csv", EVENT_FIELDS)
    _write_header("ack.csv", ACK_FIELDS)
    _write_header("scenario.csv", SCENARIO_FIELDS)

def _write_header(filename, fields):

    path = os.path.join(LOG_DIR, filename)

    if os.path.isfile(path):
        return

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

# ============================== # LOG MEASUREMENTS # ============================== #
def measurements(data):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    row = {"timestamp": timestamp}

    for key in MEASUREMENT_FIELDS[1:]:
        row[key] = data.get(key)

    _insert_db("measurements", [row[k] for k in MEASUREMENT_FIELDS])
    _insert_csv("measurements.csv", MEASUREMENT_FIELDS, row)

# ============================== # LOG INDICATOR # ============================== #
def indicator(data):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    row = {"timestamp": timestamp}

    for key in INDICATOR_FIELDS[1:]:
        row[key] = data.get(key)

    _insert_db("indicator", [row[k] for k in INDICATOR_FIELDS])
    _insert_csv("indicator.csv", INDICATOR_FIELDS, row)

# ============================== # LOG EVENT # ============================== #
def event(
    command_id,
    actuator,
    status,
    exec_time_ms,
    success,
):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    row = {
        "timestamp": timestamp,
        "command_id": command_id,
        "actuator": actuator,
        "status": status,
        "exec_time_ms": round(exec_time_ms, 2),
        "success": int(success),
    }

    _insert_db("event", [row[k] for k in EVENT_FIELDS])
    _insert_csv("event.csv", EVENT_FIELDS, row)

# ============================== # LOG ACK # ============================== #
def ack(
    command_id,
    source,
    status,
    latency_ms,
):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    row = {
        "timestamp": timestamp,
        "command_id": command_id,
        "source": source,
        "status": status,
        "latency_ms": round(latency_ms, 2),
    }

    _insert_db(
        "ack",
        [row[k] for k in ACK_FIELDS]
    )

    _insert_csv(
        "ack.csv",
        ACK_FIELDS,
        row,
    )

# ============================== # LOG SCENARIO # ============================== #
def scenario(
    controller,
    scenario_name,
    mode,
    source,
    status,
    cycle_ms,
    inputs,
    sensors,
    outputs,
):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    row = {

        "timestamp": timestamp,

        "controller": controller,

        "scenario": scenario_name,

        "mode": mode,

        "source": source,

        "status": status,

        "cycle_ms": round(cycle_ms, 2),

    }

    # ==========================
    # DIGITAL INPUT
    # ==========================

    for key in [

        "PB1","PB2","PB3","PB4",
        "PB5","PB6","PB7","PB8",

        "EM9",

        "SW10","SW11","SW12",
        "SW13","SW14",

    ]:

        row[key] = inputs.get(
            key,
            0,
        )

    # ==========================
    # SENSOR
    # ==========================

    for key in [

        "TEMP",
        "HUM",
        "RTD",
        "ANALOG",

    ]:

        row[key] = sensors.get(
            key,
            0,
        )

    # ==========================
    # DIGITAL OUTPUT
    # ==========================

    for key in [

        "LED1","LED2","LED3","LED4",
        "LED5","LED6","LED7","LED8",

        "BUZZ1","BUZZ2","BUZZ3",

        "RELAY_MOTOR",
        "RELAY_FAN",
        "RELAY_LAMP",

    ]:

        row[key] = outputs.get(
            key,
            0,
        )

    _insert_db(
        "scenario",
        [row[k] for k in SCENARIO_FIELDS]
    )

    _insert_csv(
        "scenario.csv",
        SCENARIO_FIELDS,
        row,
    )

# ============================== # DATABASE INSERT # ============================== #
def _insert_db(table, values):

    try:

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        placeholder = ",".join(["?"] * len(values))

        c.execute(
            f"INSERT INTO {table} VALUES ({placeholder})",
            values,
        )

        conn.commit()
        conn.close()

    except Exception as e:
        logger.exception("DB insert error: %s", e)

# ============================== # CSV INSERT # ============================== #
def _insert_csv(filename, fields, row):

    path = os.path.join(LOG_DIR, filename)

    try:

        with open(path, "a", newline="") as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fields,
            )

            writer.writerow(row)

    except Exception as e:
        logger.exception("CSV insert error: %s", e)