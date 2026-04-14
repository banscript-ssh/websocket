import csv
import os
import threading
from datetime import datetime
from typing import Iterable, Optional

# ======================= CONFIG =======================
_LOG_DIR = "logs"

_GATEWAY_RECEIVE_FILE = "gateway_command_receive.csv"
_CONTROLLER_APPLY_FILE = "controller_command_apply.csv"
_CONTROLLER_ACK_FILE = "controller_ack_response.csv"
_TELEMETRY_DATA_FILE = "telemetry_sensor_stream.csv"
_ACTUATOR_TIMELINE_FILE = "actuator_state_timeline.csv"

_lock = threading.Lock()

# ======================= LED DEFINITIONS =======================
LED_COLUMNS = [
    "LED1", "LED2", "LED3", "LED4",
    "LED6", "LED7",
    "BUZZ1", "BUZZ2"
]

_led_state = {led: 0 for led in LED_COLUMNS}

# ======================= UTIL =======================
def _ensure_log_file(filepath: str, header: Iterable[str]) -> None:
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)

def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# ======================= GATEWAY RECEIVE LOGGER =======================
def log_receive_command(
    command_id: str,
    source_ip: str,
    source_port: int,
    parsed_keys: Iterable[str],
    raw_payload: str,
) -> None:
    filepath = os.path.join(_LOG_DIR, _GATEWAY_RECEIVE_FILE)
    header = [
        "gateway_receive_ts",
        "command_id",
        "source_ip",
        "source_port",
        "parsed_keys",
        "raw_payload",
    ]

    with _lock:
        _ensure_log_file(filepath, header)
        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                _timestamp(),
                command_id,
                source_ip,
                source_port,
                ",".join(parsed_keys),
                raw_payload,
            ])

# ======================= CONTROLLER APPLY LOGGER =======================
def log_apply_command(
    command_id: str,
    applied_keys: Iterable[str],
    success: bool,
    exec_time_ms: float,
    error: Optional[str] = None,
) -> None:
    filepath = os.path.join(_LOG_DIR, _CONTROLLER_APPLY_FILE)
    header = [
        "controller_apply_ts",
        "command_id",
        "applied_keys",
        "success",
        "exec_time_ms",
        "error",
    ]

    with _lock:
        _ensure_log_file(filepath, header)
        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                _timestamp(),
                command_id,
                ",".join(applied_keys),
                success,
                f"{exec_time_ms:.3f}",
                error or "",
            ])

# ======================= CONTROLLER ACK LOGGER =======================
def log_ack(
    command_id: str,
    source: str,
    status: str,
    latency_ms: Optional[float] = None,
) -> None:
    filepath = os.path.join(_LOG_DIR, _CONTROLLER_ACK_FILE)
    header = [
        "controller_ack_ts",
        "command_id",
        "source",
        "status",
        "latency_ms",
    ]

    with _lock:
        _ensure_log_file(filepath, header)
        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                _timestamp(),
                command_id,
                source,
                status,
                f"{latency_ms:.3f}" if latency_ms else "",
            ])

# ======================= TELEMETRY DATA LOGGER =======================
def log_data(data: dict) -> None:
    filepath = os.path.join(_LOG_DIR, _TELEMETRY_DATA_FILE)

    base_fields = [
        "telemetry_ts",
        "source",
        "TEMP",
        "HUM",
        "ANALOG",
        "RTD",
    ]

    led_fields = [k for k in data.keys() if k.startswith("LED")]
    header = base_fields + led_fields

    row = {
        "telemetry_ts": _timestamp(),
        "source": data.get("source"),
        "TEMP": data.get("TEMP"),
        "HUM": data.get("HUM"),
        "ANALOG": data.get("ANALOG"),
        "RTD": data.get("RTD"),
    }

    for led in led_fields:
        row[led] = data.get(led)

    with _lock:
        _ensure_log_file(filepath, header)
        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writerow(row)

# ======================= ACTUATOR STATE TIMELINE LOGGER =======================
def log_led_state_wide(command: dict) -> None:
    filepath = os.path.join(_LOG_DIR, _ACTUATOR_TIMELINE_FILE)
    header = ["actuator_state_ts"] + LED_COLUMNS

    with _lock:
        _ensure_log_file(filepath, header)

        for led in LED_COLUMNS:
            if led in command:
                _led_state[led] = int(command[led])

        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [_timestamp()] + [_led_state[led] for led in LED_COLUMNS]
            )