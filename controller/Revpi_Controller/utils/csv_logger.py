
import csv
import os
import threading
import time
from datetime import datetime
from typing import Iterable, Optional

# ======================= CONFIG =======================
_LOG_DIR = "logs"

_GATEWAY_RECEIVE_FILE = "gateway_command_receive.csv"
_CONTROLLER_APPLY_FILE = "controller_command_apply.csv"
_CONTROLLER_ACK_FILE = "controller_ack_response.csv"
_TELEMETRY_DATA_FILE = "telemetry_sensor_stream.csv"
_ACTUATOR_TIMELINE_FILE = "actuator_state_timeline.csv"
_TELEMETRY_INTERVAL_FILE = "telemetry_interval_log.csv"

_lock = threading.Lock()

# ======================= ACTUATOR DEFINITIONS =======================
LED_COLUMNS = ["BUZZ1", "BUZZ2", "BUZZ3",
               "LED1", "LED2", "LED3", "LED4", "LED5",
               "LED6", "LED7", "LED8", "LED9",
               "LED10", "LED11"]

_led_state = {device: 0 for device in LED_COLUMNS}
_last_telemetry_epoch = None

# ======================= UTIL =======================
def _ensure_log_file(filepath: str, header: Iterable[str]) -> None:
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(header)

def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def _append_csv(filepath: str, header: Iterable[str], row: list) -> None:
    with _lock:
        _ensure_log_file(filepath, header)
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)

# ======================= GATEWAY RECEIVE LOGGER =======================
def log_receive_command(command_id: str,
                        source_ip: str,
                        source_port: int,
                        parsed_keys: Iterable[str],
                        raw_payload: str) -> None:
    filepath = os.path.join(_LOG_DIR, _GATEWAY_RECEIVE_FILE)

    header = ["gateway_receive_ts", "gateway_receive_epoch", "command_id",
              "source_ip", "source_port", "parsed_keys",
              "payload_size", "raw_payload"]

    row = [_timestamp(), time.time(), command_id,
           source_ip, source_port,
           ",".join(parsed_keys),
           len(raw_payload.encode()),
           raw_payload]
    _append_csv(filepath, header, row)

# ======================= CONTROLLER APPLY LOGGER =======================
def log_apply_command(command_id: str,
                      applied_keys: Iterable[str],
                      success: bool,
                      exec_time_ms: float,
                      error: Optional[str] = None) -> None:
    filepath = os.path.join(_LOG_DIR, _CONTROLLER_APPLY_FILE)

    header = ["controller_apply_ts", "controller_apply_epoch",
              "command_id", "applied_keys",
              "success", "exec_time_ms", "error"]

    row = [_timestamp(), time.time(),
           command_id,
           ",".join(applied_keys),
           success,
           f"{exec_time_ms:.3f}",
           error or ""]
    _append_csv(filepath, header, row)

# ======================= CONTROLLER ACK LOGGER =======================
def log_ack(command_id: str,
            source: str,
            status: str,
            latency_ms: Optional[float] = None) -> None:
    filepath = os.path.join(_LOG_DIR, _CONTROLLER_ACK_FILE)

    header = ["controller_ack_ts", "controller_ack_epoch",
              "command_id", "source",
              "status", "latency_ms"]
    row = [_timestamp(), time.time(),
           command_id,
           source,
           status,
           f"{latency_ms:.3f}" if latency_ms is not None else ""]
    _append_csv(filepath, header, row)

# ======================= TELEMETRY DATA LOGGER =======================
def log_data(data: dict) -> None:
    filepath = os.path.join(_LOG_DIR, _TELEMETRY_DATA_FILE)
    base_fields = ["telemetry_ts", "telemetry_epoch",
                   "source", "TEMP", "HUM",
                   "ANALOG", "RTD"]

    actuator_fields = [key for key in data if key in LED_COLUMNS]
    header = base_fields + actuator_fields

    row = {
        "telemetry_ts": _timestamp(),
        "telemetry_epoch": time.time(),
        "source": data.get("source"),
        "TEMP": data.get("TEMP"),
        "HUM": data.get("HUM"),
        "ANALOG": data.get("ANALOG"),
        "RTD": data.get("RTD")
    }
    row.update({device: data.get(device) for device in actuator_fields})

    with _lock:
        _ensure_log_file(filepath, header)
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=header).writerow(row)

# ======================= ACTUATOR STATE TIMELINE LOGGER =======================
def log_led_state_wide(command: dict) -> None:
    filepath = os.path.join(_LOG_DIR, _ACTUATOR_TIMELINE_FILE)
    header = ["actuator_state_ts", "actuator_state_epoch"] + LED_COLUMNS
    for device in LED_COLUMNS:
        if device in command:
            _led_state[device] = int(command[device])
    row = [_timestamp(), time.time()] + [_led_state[device] for device in LED_COLUMNS]
    _append_csv(filepath, header, row)

# ======================= TELEMETRY INTERVAL LOGGER =======================
def log_telemetry_interval() -> None:
    global _last_telemetry_epoch
    epoch_now = time.time()
    delta_ms = ""

    if _last_telemetry_epoch is not None:
        delta_ms = (epoch_now - _last_telemetry_epoch) * 1000
    _last_telemetry_epoch = epoch_now
    filepath = os.path.join(_LOG_DIR, _TELEMETRY_INTERVAL_FILE)

    header = ["timestamp", "epoch_time", "delta_t_ms"]

    row = [_timestamp(),
           epoch_now,
           f"{delta_ms:.3f}" if delta_ms != "" else ""]
    _append_csv(filepath, header, row)
