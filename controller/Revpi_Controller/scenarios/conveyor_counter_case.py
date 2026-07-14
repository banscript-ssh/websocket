from revpi.input_manager import get_input
from revpi.data_provider import apply_control_command

# =====================================
# TARGET COUNTER
# =====================================

TARGET_COUNT = 10

counter = 0
running = False
alarm = False

last_pb1 = False
last_pb2 = False
last_pb3 = False
last_pb4 = False

last_proximity = False


# =====================================
# INITIALIZE
# =====================================

async def initialize():

    global counter
    global running
    global alarm

    counter = 0
    running = False
    alarm = False

    print("[SCENARIO] Conveyor Counter Started")


# =====================================
# UPDATE
# =====================================

async def update():

    global counter
    global running
    global alarm

    global last_pb1
    global last_pb2
    global last_pb3
    global last_pb4
    global last_proximity

    buttons = get_input()

    pb1 = bool(buttons["PB1"])
    pb2 = bool(buttons["PB2"])
    pb3 = bool(buttons["PB3"])
    pb4 = bool(buttons["PB4"])

    proximity = bool(buttons["PROXIMITY"])

    # =================================
    # START
    # =================================

    if pb1 and not last_pb1:

        running = True

    # =================================
    # STOP
    # =================================

    if pb2 and not last_pb2:

        running = False

    # =================================
    # RESET COUNTER
    # =================================

    if pb3 and not last_pb3:

        counter = 0
        alarm = False

    # =================================
    # ACK ALARM
    # =================================

    if pb4 and not last_pb4:

        alarm = False

    # =================================
    # UPDATE BUTTON STATE
    # =================================

    last_pb1 = pb1
    last_pb2 = pb2
    last_pb3 = pb3
    last_pb4 = pb4

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

    # =================================
    # EMERGENCY
    # =================================

    if buttons["EM9"]:

        state["LED6"] = 1

        apply_control_command(state)

        return

    # =================================
    # MOTOR RUNNING
    # =================================

    if running:

        state["LED1"] = 1
        state["LED3"] = 1
        state["RELAY_MOTOR"] = 1

    # =================================
    # OBJECT DETECTED
    # =================================

    if proximity:

        state["LED2"] = 1

    # Rising Edge Detection
    if proximity and not last_proximity and running:

        counter += 1

        print(f"[COUNTER] {counter}")

    last_proximity = proximity

    # =================================
    # TARGET
    # =================================

    if counter >= TARGET_COUNT:

        running = False
        alarm = True

    # =================================
    # ALARM
    # =================================

    if alarm:

        state["LED4"] = 1
        state["BUZZ1"] = 1

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

    print("[SCENARIO] Conveyor Counter Stopped")