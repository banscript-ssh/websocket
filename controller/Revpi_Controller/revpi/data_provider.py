# ============================== # IMPORT LIBRARY # ============================== #
import time
from typing import Dict

from revpi.sensor import (
    read_signal_generator,
    read_rtd_pt1000,
)
from revpi.modbus import read_md02
from revpi.actuator import control_actuators

from utils.csv_logger import (
    log_apply_command,
)

# ============================== # INIT REVPI (SHARED, JANGAN BUAT INSTANCE BARU) # ============================== #
from revpi.rpi_core import rpi

# ============================== # CONTROL MODE # ============================== #
def get_control_mode() -> str:
    """
    SW10 Selector

    0 = LOCAL
    1 = REMOTE
    """

    return "REMOTE" if rpi.io.I_10.value else "LOCAL"

# ============================== # SENSOR ACQUISITION # ============================== #
def read_all():

    raw_uA, mA = read_signal_generator()
    raw_rtd, rtd = read_rtd_pt1000()
    temp, hum = read_md02()
    
    print(
        f"I1={rpi.io.I_1.value} "
        f"I2={rpi.io.I_2.value} "
        f"I3={rpi.io.I_3.value} "
        f"I4={rpi.io.I_4.value} "
        f"I5={rpi.io.I_5.value} "
        f"I6={rpi.io.I_6.value} "
        f"I7={rpi.io.I_7.value} "
        f"I8={rpi.io.I_8.value}"
)
    return {

        # Sensor
        "ANALOG": mA,
        "RTD": rtd,
        "TEMP": temp,
        "HUM": hum,

        # Digital Input
        # NOTE: PB1-PB4 = tombol NO (Normally Open)  -> idle=0, ditekan=1
        #       PB5-PB8 = tombol NC (Normally Closed) -> idle=1, ditekan=0
        # Supaya semantik "1 = ditekan" konsisten untuk SEMUA tombol
        # (dan actuator.py/scenario tidak perlu tahu soal NO/NC sama
        # sekali), PB5-PB8 di-invert di sini, di titik pembacaan.
        "PB1": int(rpi.io.I_1.value),
        "PB2": int(rpi.io.I_2.value),
        "PB3": int(rpi.io.I_3.value),
        "PB4": int(rpi.io.I_4.value),
        "PB5": int(not rpi.io.I_5.value),
        "PB6": int(not rpi.io.I_6.value),
        "PB7": int(not rpi.io.I_7.value),
        "PB8": int(not rpi.io.I_8.value),

        "EM9": int(rpi.io.I_9.value),

        "SW10": int(rpi.io.I_10.value),
        "SW11": int(rpi.io.I_11.value),
        # SW12-SW14 = selector NC (idle=1, aktif=0), sama seperti PB5-PB8.
        # Di-invert di sini supaya "1 = aktif/switch dinyalakan", jadi
        # RELAY_MOTOR/RELAY_FAN/RELAY_LAMP defaultnya OFF (0) saat idle,
        # dan baru ON saat switch-nya benar-benar digeser/diaktifkan.
        "SW12": int(not rpi.io.I_12.value),
        "SW13": int(not rpi.io.I_13.value),
        "SW14": int(not rpi.io.I_14.value),
    }

# ============================== # WRITE DIGITAL OUTPUT # ============================== #
def write_outputs(state: dict):

    print("[WRITE REQUEST]", state)

    rpi.io.O_1.value = state.get("BUZZ1", 0)
    rpi.io.O_2.value = state.get("BUZZ2", 0)
    rpi.io.O_3.value = state.get("BUZZ3", 0)

    rpi.io.O_4.value = state.get("LED1", 0)
    rpi.io.O_5.value = state.get("LED2", 0)
    rpi.io.O_6.value = state.get("LED3", 0)
    rpi.io.O_7.value = state.get("LED4", 0)
    rpi.io.O_8.value = state.get("LED5", 0)
    rpi.io.O_9.value = state.get("LED6", 0)
    rpi.io.O_10.value = state.get("LED7", 0)
    rpi.io.O_11.value = state.get("LED8", 0)

    rpi.io.O_12.value = state.get("RELAY_MOTOR", 0)
    rpi.io.O_13.value = state.get("RELAY_FAN", 0)
    rpi.io.O_14.value = state.get("RELAY_LAMP", 0)

    rpi.writeprocimg()

    print("[WRITE RESULT]", get_actuator_state())

# ============================== #
# APPLY OUTPUT STATE
# ============================== #
def apply_output_state(state):

    current_state = get_actuator_state()

    new_state = current_state.copy()

    for key, value in state.items():

        if key in new_state:

            new_state[key] = int(value)

    write_outputs(new_state)

    return new_state
    
# ============================== # LOCAL HARDWARE CONTROL # ============================== #
# ============================== # LOCAL HARDWARE CONTROL # ============================== #
def process_actuators():
    """
    Digital Input
        ↓
    Logic Process
        ↓
    Digital Output
    """

    buttons = read_all()

    state = control_actuators(buttons)

    return {
        **buttons,
        **state,
    }
    
# ============================== # APPLY LOCAL CONTROL # ============================== #
def apply_local_control():

    if get_control_mode() != "LOCAL":
        return None

    result = process_actuators()

    output_state = {
        key: value
        for key, value in result.items()
        if key.startswith(("LED", "BUZZ", "RELAY"))
    }

    write_outputs(output_state)

    return result

# ============================== # READ OUTPUT STATE # ============================== #
def get_actuator_state():

    return {
        "BUZZ1": int(rpi.io.O_1.value),
        "BUZZ2": int(rpi.io.O_2.value),
        "BUZZ3": int(rpi.io.O_3.value),

        "LED1": int(rpi.io.O_4.value),
        "LED2": int(rpi.io.O_5.value),
        "LED3": int(rpi.io.O_6.value),
        "LED4": int(rpi.io.O_7.value),
        "LED5": int(rpi.io.O_8.value),
        "LED6": int(rpi.io.O_9.value),
        "LED7": int(rpi.io.O_10.value),
        "LED8": int(rpi.io.O_11.value),

        "RELAY_MOTOR": int(rpi.io.O_12.value),
        "RELAY_FAN": int(rpi.io.O_13.value),
        "RELAY_LAMP": int(rpi.io.O_14.value),
    }

# ============================== # REMOTE DASHBOARD CONTROL # ============================== #
def apply_control_command(
    cmd: dict,
    command_id: str = "LOCAL",
) -> Dict:

    start_time = time.perf_counter()

    if get_control_mode() != "REMOTE":

        exec_time_ms = (
            time.perf_counter() - start_time
        ) * 1000

        log_apply_command(
            command_id=command_id,
            applied_keys=[],
            success=False,
            exec_time_ms=exec_time_ms,
            error="LOCAL_MODE",
        )

        return {
            "command_id": command_id,
            "applied_keys": [],
            "success": False,
            "exec_time_ms": exec_time_ms,
            "error": "LOCAL_MODE",
        }

    applied_keys = []

    try:

        apply_output_state(cmd)

        applied_keys = list(cmd.keys())

        success = True
        error = None

    except Exception as e:

        applied_keys = []

        success = False
        error = str(e)

    exec_time_ms = (
        time.perf_counter() - start_time
    ) * 1000

    log_apply_command(
        command_id=command_id,
        applied_keys=applied_keys,
        success=success,
        exec_time_ms=exec_time_ms,
        error=error,
    )

    return {
        "command_id": command_id,
        "applied_keys": applied_keys,
        "success": success,
        "exec_time_ms": exec_time_ms,
        "error": error,
    }