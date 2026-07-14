# ==============================
# IMPORT LIBRARY
# ==============================

from revpi.input_manager import get_input
from revpi.data_provider import apply_control_command


# ==============================
# INITIALIZE
# ==============================

async def initialize():

    print("[SCENARIO] LOGIC GATE STARTED")


# ==============================
# UPDATE
# ==============================

async def update():

    buttons = get_input()

    state = {}

    # ==========================
    # INPUT
    # ==========================

    A = bool(buttons["PB1"])
    B = bool(buttons["PB2"])

    # ==========================
    # LOGIC GATE
    # ==========================

    state["LED1"] = int(A and B)            # AND

    state["LED2"] = int(A or B)             # OR

    state["LED3"] = int(A ^ B)              # XOR

    state["LED4"] = int(not (A and B))      # NAND

    state["LED5"] = int(not (A or B))       # NOR

    state["LED6"] = int(not A)              # NOT

    state["LED7"] = int(buttons["SW10"])    # Hardware / Dashboard Indicator

    state["LED8"] = int(not (A ^ B))        # XNOR

    # ==========================
    # EMERGENCY
    # ==========================

    if buttons["EM9"]:

        state = {

            "LED1":0,
            "LED2":0,
            "LED3":0,
            "LED4":0,
            "LED5":0,
            "LED6":1,
            "LED7":0,
            "LED8":0,

            "BUZZ1":0,
            "BUZZ2":0,
            "BUZZ3":0,

            "RELAY_MOTOR":0,
            "RELAY_FAN":0,
            "RELAY_LAMP":0
        }

    apply_control_command(state)


# ==============================
# SHUTDOWN
# ==============================

async def shutdown():

    apply_control_command({

        "LED1":0,
        "LED2":0,
        "LED3":0,
        "LED4":0,
        "LED5":0,
        "LED6":0,
        "LED7":0,
        "LED8":0,

        "BUZZ1":0,
        "BUZZ2":0,
        "BUZZ3":0,

        "RELAY_MOTOR":0,
        "RELAY_FAN":0,
        "RELAY_LAMP":0

    })

    print("[SCENARIO] LOGIC GATE STOPPED")