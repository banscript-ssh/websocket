from revpi.input_manager import get_input
from revpi.data_provider import (
    read_all,
    apply_control_command
)

# =====================================
# SETPOINT
# =====================================

TEMP_LOW = 28.0
TEMP_HIGH = 32.0

HUM_LOW = 40.0
HUM_HIGH = 80.0

running = False

last_pb1 = False
last_pb2 = False


async def initialize():

    global running

    running = False

    print("[SCENARIO] MINI PROCESS STARTED")


async def update():

    global running
    global last_pb1
    global last_pb2

    buttons = get_input()

    sensor = read_all()

    pb1 = bool(buttons["PB1"])
    pb2 = bool(buttons["PB2"])

    # ---------------------------------
    # START
    # ---------------------------------

    if pb1 and not last_pb1:
        running = True

    # ---------------------------------
    # STOP
    # ---------------------------------

    if pb2 and not last_pb2:
        running = False

    last_pb1 = pb1
    last_pb2 = pb2

    state = {

        "LED1":0,
        "LED2":0,
        "LED3":0,
        "LED4":0,
        "LED5":0,
        "LED6":0,
        "LED7":int(buttons["SW10"]),
        "LED8":0,

        "BUZZ1":0,
        "BUZZ2":0,
        "BUZZ3":0,

        "RELAY_MOTOR":0,
        "RELAY_FAN":0,
        "RELAY_LAMP":0
    }

    # ---------------------------------
    # EMERGENCY
    # ---------------------------------

    if buttons["EM9"]:

        state["LED6"] = 1

        apply_control_command(state)

        return

    # ---------------------------------
    # STOP MODE
    # ---------------------------------

    if not running:

        apply_control_command(state)

        return

    # ---------------------------------
    # RUNNING
    # ---------------------------------

    state["LED5"] = 1

    temperature = sensor["temperature"]
    humidity = sensor["humidity"]

    # =================================
    # TEMPERATURE CONTROL
    # =================================

    if temperature < TEMP_LOW:

        # Heating

        state["LED2"] = 1

        state["RELAY_LAMP"] = 1

    elif temperature > TEMP_HIGH:

        # Cooling

        state["LED3"] = 1

        state["RELAY_FAN"] = 1

    else:

        state["LED8"] = 1

    # =================================
    # HUMIDITY ALARM
    # =================================

    if humidity < HUM_LOW or humidity > HUM_HIGH:

        state["LED4"] = 1

        state["BUZZ1"] = 1

    # =================================
    # MONITOR
    # =================================

    state["LED1"] = 1

    apply_control_command(state)


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

    print("[SCENARIO] MINI PROCESS STOPPED")