# ==============================
# IMPORT LIBRARY
# ==============================

import time

from revpi.input_manager import get_input
from revpi.actuator import control_actuators
from revpi.data_provider import (
    apply_output_state,
    read_all,
    get_control_mode,
)

from revpi.client_revpi import (
    CONTROLLER_ID,
)

from revpi.logging import (
    scenario,
)

# ==============================
# INITIALIZE
# ==============================

async def initialize():

    print("[SCENARIO] IO TEST STARTED")


# ==============================
# UPDATE
# ==============================

async def update():

    start_time = time.perf_counter()

    # =========================
    # INPUT
    # =========================

    buttons = get_input()

    sensors = read_all()

    mode = get_control_mode()

    # DEBUG
    print("[INPUT ]", buttons)

    # =========================
    # PROCESS LOGIC
    # =========================

    state = control_actuators(buttons)

    # DEBUG
    print("[OUTPUT]", state)

    # =========================
    # EMERGENCY STOP
    # =========================

    if not buttons["EM9"]:

        state["BUZZ1"] = 0
        state["BUZZ2"] = 0
        state["BUZZ3"] = 0

        state["LED1"] = 0
        state["LED2"] = 0
        state["LED3"] = 0
        state["LED4"] = 0
        state["LED5"] = 0

        state["LED7"] = 0
        state["LED8"] = 0

        state["RELAY_MOTOR"] = 0
        state["RELAY_FAN"] = 0
        state["RELAY_LAMP"] = 0

        # Emergency Indicator
        state["LED6"] = 1

    # =========================
    # WRITE OUTPUT
    # =========================

    if mode == "LOCAL":

        apply_output_state(state)

    else:

        print(
            "[SKIP WRITE] Mode REMOTE"
        )

    # =========================
    # SCENARIO LOGGER
    # =========================

    cycle_ms = (
        time.perf_counter() - start_time
    ) * 1000

    scenario(

        controller=CONTROLLER_ID,

        scenario_name="IO",

        mode=mode,

        source=(
            "Dashboard"
            if mode == "REMOTE"
            else "Hardware"
        ),

        status=(
            "EMERGENCY"
            if not buttons["EM9"]
            else "RUNNING"
        ),

        cycle_ms=cycle_ms,

        inputs=buttons,

        sensors=sensors,

        outputs=state,
    )


# ==============================
# SHUTDOWN
# ==============================

async def shutdown():

    apply_output_state({

        "BUZZ1":0,
        "BUZZ2":0,
        "BUZZ3":0,

        "LED1":0,
        "LED2":0,
        "LED3":0,
        "LED4":0,
        "LED5":0,
        "LED6":0,
        "LED7":0,
        "LED8":0,

        "RELAY_MOTOR":0,
        "RELAY_FAN":0,
        "RELAY_LAMP":0,

    })

    print("[SCENARIO] IO TEST STOPPED")