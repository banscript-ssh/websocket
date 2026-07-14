import time

from revpi.input_manager import get_input
from revpi.data_provider import apply_control_command

# ==========================================================
# TRAFFIC LIGHT STATE
# ==========================================================

STATE_RED = 0
STATE_RED_YELLOW = 1
STATE_GREEN = 2
STATE_YELLOW = 3

current_state = STATE_RED

running = False
paused = False

state_timer = time.monotonic()

# ==========================================================
# EDGE DETECTION
# ==========================================================

last_pb1 = False
last_pb2 = False
last_pb3 = False
last_pb4 = False

# ==========================================================
# TIMER
# ==========================================================

RED_TIME = 5
RED_YELLOW_TIME = 2
GREEN_TIME = 5
YELLOW_TIME = 2


async def initialize():

    global running
    global paused
    global current_state
    global state_timer

    running = False
    paused = False
    current_state = STATE_RED
    state_timer = time.monotonic()

    print("[Traffic] Initialized")


async def update():

    global running
    global paused
    global current_state
    global state_timer

    global last_pb1
    global last_pb2
    global last_pb3
    global last_pb4

    buttons = get_input()

    pb1 = bool(buttons["PB1"])
    pb2 = bool(buttons["PB2"])
    pb3 = bool(buttons["PB3"])
    pb4 = bool(buttons["PB4"])

    # ======================================================
    # START
    # ======================================================

    if pb1 and not last_pb1:

        running = True
        paused = False

    # ======================================================
    # STOP
    # ======================================================

    if pb2 and not last_pb2:

        running = False

    # ======================================================
    # PAUSE
    # ======================================================

    if pb3 and not last_pb3:

        paused = not paused

    # ======================================================
    # RESET
    # ======================================================

    if pb4 and not last_pb4:

        current_state = STATE_RED
        state_timer = time.monotonic()

    # ======================================================
    # UPDATE LAST BUTTON
    # ======================================================

    last_pb1 = pb1
    last_pb2 = pb2
    last_pb3 = pb3
    last_pb4 = pb4

    # ======================================================
    # EMERGENCY
    # ======================================================

    if buttons["EM9"]:

        apply_control_command({

            "LED1":0,
            "LED2":0,
            "LED3":0,

            "LED4":0,
            "LED5":0,
            "LED6":1,
            "LED7":int(buttons["SW10"]),
            "LED8":0,

            "RELAY_MOTOR":0,
            "RELAY_FAN":0,
            "RELAY_LAMP":0,

            "BUZZ1":0,
            "BUZZ2":0,
            "BUZZ3":0

        })

        return

    # ======================================================
    # STOP MODE
    # ======================================================

    if not running:

        apply_control_command({

            "LED1":0,
            "LED2":0,
            "LED3":0,

            "LED4":0,
            "LED5":0,
            "LED6":0,
            "LED7":int(buttons["SW10"]),
            "LED8":0,

            "RELAY_MOTOR":0,
            "RELAY_FAN":0,
            "RELAY_LAMP":0,

            "BUZZ1":0,
            "BUZZ2":0,
            "BUZZ3":0

        })

        return

    # ======================================================
    # PAUSE
    # ======================================================

    if paused:

        return

    elapsed = time.monotonic() - state_timer

    state = {

        "LED1":0,
        "LED2":0,
        "LED3":0,

        "LED4":0,
        "LED5":0,
        "LED6":0,
        "LED7":int(buttons["SW10"]),
        "LED8":0,

        "RELAY_MOTOR":0,
        "RELAY_FAN":0,
        "RELAY_LAMP":1,

        "BUZZ1":0,
        "BUZZ2":0,
        "BUZZ3":0
    }

    # ======================================================
    # RED
    # ======================================================

    if current_state == STATE_RED:

        state["LED1"] = 1

        if elapsed >= RED_TIME:

            current_state = STATE_RED_YELLOW
            state_timer = time.monotonic()

    # ======================================================
    # RED + YELLOW
    # ======================================================

    elif current_state == STATE_RED_YELLOW:

        state["LED1"] = 1
        state["LED2"] = 1

        if elapsed >= RED_YELLOW_TIME:

            current_state = STATE_GREEN
            state_timer = time.monotonic()

    # ======================================================
    # GREEN
    # ======================================================

    elif current_state == STATE_GREEN:

        state["LED3"] = 1
        state["RELAY_MOTOR"] = 1

        if elapsed >= GREEN_TIME:

            current_state = STATE_YELLOW
            state_timer = time.monotonic()

    # ======================================================
    # YELLOW
    # ======================================================

    elif current_state == STATE_YELLOW:

        state["LED2"] = 1

        if elapsed >= YELLOW_TIME:

            current_state = STATE_RED
            state_timer = time.monotonic()

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

        "RELAY_MOTOR":0,
        "RELAY_FAN":0,
        "RELAY_LAMP":0,

        "BUZZ1":0,
        "BUZZ2":0,
        "BUZZ3":0

    })

    print("[Traffic] Shutdown")