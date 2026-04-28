import csv
import os
import threading
from datetime import datetime
from typing import Iterable, Optional

# ======================= CONFIG =======================
_LOG_DIR = "logs"

_RECEIVE_FILE = "receive_command_log.csv"
_APPLY_FILE = "apply_command_log.csv"
_LED_WIDE_FILE = "led_state_wide.csv"

_lock = threading.Lock()

# ======================= LED DEFINITIONS =======================
LED_COLUMNS = [
    "LED1", "LED2", "LED3", "LED4",
    "LED6", "LED7",
    "BUZZ1", "BUZZ2"
]

# Persisted LED state (tidak reset tiap baris)
_led_state = {led: 0 for led in LED_COLUMNS}


# ======================= UTIL =======================
def _ensure_log_file(filepath: str, header: Iterable[str]) -> None:
    """
    Create CSV file with header if it does not exist
    """
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)


def _timestamp() -> str:
    """
    Timestamp format:
    YYYY-MM-DD HH:MM:SS.mmm
    Example: 2026-01-11 16:48:58.237
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


# ======================= RECEIVE LOGGER =======================
def log_receive_command(
    command_id: str,
    source_ip: str,
    source_port: int,
    parsed_keys: Iterable[str],
    raw_payload: str,
) -> None:
    """
    Log incoming control command (receive side)
    """
    filepath = os.path.join(_LOG_DIR, _RECEIVE_FILE)
    header = [
        "timestamp_receive",
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
            writer.writerow(
                [
                    _timestamp(),
                    command_id,
                    source_ip,
                    source_port,
                    ",".join(parsed_keys),
                    raw_payload,
                ]
            )


# ======================= APPLY LOGGER =======================
def log_apply_command(
    command_id: str,
    applied_keys: Iterable[str],
    success: bool,
    exec_time_ms: float,
    error: Optional[str] = None,
) -> None:
    """
    Log execution of control command (apply side)
    """
    filepath = os.path.join(_LOG_DIR, _APPLY_FILE)
    header = [
        "timestamp_apply",
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
            writer.writerow(
                [
                    _timestamp(),
                    command_id,
                    ",".join(applied_keys),
                    success,
                    f"{exec_time_ms:.3f}",
                    error or "",
                ]
            )


# ======================= LED STATE LOGGER (WIDE TABLE) =======================
def log_led_state_wide(command: dict) -> None:
    """
    Log LED state in wide-table format:
    timestamp, LED1, LED2, ..., BUZZ2
    """

    filepath = os.path.join(_LOG_DIR, _LED_WIDE_FILE)
    header = ["timestamp"] + LED_COLUMNS

    with _lock:
        _ensure_log_file(filepath, header)

        # Update LED state from command
        for led in LED_COLUMNS:
            if led in command:
                _led_state[led] = int(command[led])

        with open(filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [_timestamp()] + [_led_state[led] for led in LED_COLUMNS]
            )
