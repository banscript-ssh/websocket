# ============================== # IMPORT LIBRARY # ==============================
import revpimodio2
from revpi.sensor import read_signal_generator, read_rtd_pt1000
from revpi.modbus import read_md02
from revpi.actuator import control_actuators
import time
from typing import Dict
from utils.csv_logger import log_apply_command,  log_led_state_wide

# ============================== # INIT REVPI # ==============================
rpi = revpimodio2.RevPiModIO(autorefresh=True)

# ======================= # MONITORING (SENSOR) # =======================
def read_all():
    # RevPi analog
    raw_uA, mA = read_signal_generator()
    raw_rtd, rtd = read_rtd_pt1000()

    # MD02
    temp, hum = read_md02()

    return {
        "ANALOG": mA,
        "RTD": rtd,
        "TEMP": temp,
        "HUM": hum
    }

def process_actuators():
    """
    Baca input -> proses logika -> tulis output
    (5 Push Button -> 5 LED)
    """
    buttons = {
        "PB1": int(rpi.io.I_1.value),
        "PB2": int(rpi.io.I_2.value),
        "PB3": int(rpi.io.I_3.value),
        "PB4": int(rpi.io.I_4.value),
        "PB5": int(rpi.io.I_5.value),
        "PB6": int(rpi.io.I_6.value),
        "PB7": int(rpi.io.I_7.value),
        "PB8": int(rpi.io.I_8.value),
        "PB9": int(rpi.io.I_9.value),
        "PB10": int(rpi.io.I_10.value),
    }

    state = control_actuators(buttons)

    rpi.io.O_1.value = state["LED1"]
    rpi.io.O_2.value = state["LED2"]
    rpi.io.O_3.value = state["LED3"]
    rpi.io.O_4.value = state["LED4"]
    rpi.io.O_5.value = state["BUZZ1"]
    rpi.io.O_6.value = state["LED6"]
    rpi.io.O_7.value = state["LED7"]
    # rpi.io.O_8.value = state["LED8"]
    # rpi.io.O_9.value = state["LED9"]
    rpi.io.O_10.value = state["BUZZ2"]
    

    return {
        **buttons,
        **state
    }

def get_actuator_state():
    """
    Baca status output fisik RevPi (ground truth untuk GWeb)
    """
    return {
        "LED1": int(rpi.io.O_1.value),
        "LED2": int(rpi.io.O_2.value),
        "LED3": int(rpi.io.O_3.value),
        "LED4": int(rpi.io.O_4.value),
        "BUZZ1": int(rpi.io.O_5.value),  
        "LED6": int(rpi.io.O_6.value),
        "LED7": int(rpi.io.O_7.value),
        # "LED8": int(rpi.io.O_8.value),
        # "LED9": int(rpi.io.O_9.value),
        "BUZZ2": int(rpi.io.O_10.value),
        # tambah jika perlu
    }

def apply_control_command(cmd: dict, command_id: str) -> Dict:
    """
    Apply control command from GWeb (event-based control).
    This function ONLY writes to hardware and logs APPLY time.
    """

    start_time = time.perf_counter()
    applied_keys = []

    try:
        if "LED1" in cmd:
            rpi.io.O_1.value = int(cmd["LED1"])
            applied_keys.append("LED1")

        if "LED2" in cmd:
            rpi.io.O_2.value = int(cmd["LED2"])
            applied_keys.append("LED2")

        if "LED3" in cmd:
            rpi.io.O_3.value = int(cmd["LED3"])
            applied_keys.append("LED3")

        if "LED4" in cmd:
            rpi.io.O_4.value = int(cmd["LED4"])
            applied_keys.append("LED4")

        if "BUZZ1" in cmd:
            rpi.io.O_5.value = int(cmd["BUZZ1"])
            applied_keys.append("BUZZ1")

        if "LED6" in cmd:
            rpi.io.O_6.value = int(cmd["LED6"])
            applied_keys.append("LED6")

        if "LED7" in cmd:
            rpi.io.O_7.value = int(cmd["LED7"])
            applied_keys.append("LED7")

        if "BUZZ2" in cmd:
            rpi.io.O_10.value = int(cmd["BUZZ2"])
            applied_keys.append("BUZZ2")

        success = True
        error = None

    except Exception as e:
        success = False
        error = str(e)

    exec_time_ms = (time.perf_counter() - start_time) * 1000

    # ===================== APPLY LOGGER (CSV) =====================
    log_apply_command(
        command_id=command_id,
        applied_keys=applied_keys,
        success=success,
        exec_time_ms=exec_time_ms,
        error=error,
    )

    # ===================== LED STATE LOGGER (WIDE TABLE) =====================
    log_led_state_wide(cmd)

    return {
        "command_id": command_id,
        "applied_keys": applied_keys,
        "success": success,
        "exec_time_ms": exec_time_ms,
        "error": error,
    }
