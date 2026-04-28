def control_actuators(buttons):
    """
    buttons : dict dari data_provider.read_buttons()
              contoh: {"PB1":0, "PB2":1, ..., "PB5":0}
    return  : dict state output LED
    """

    state = {
        "LED1": 0,
        "LED2": 0,
        "LED3": 0,
        "LED4": 0,
        "BUZZ1": 0,
        "LED6": 0,
        "LED7": 0,
        # "LED8": 0,
        # "LED9": 0,
        "BUZZ2": 0,
    }

    # PLC-style direct control (momentary)
    state["LED1"] = 1 if buttons["PB1"] == 1 else 0
    state["LED2"] = 1 if buttons["PB2"] == 1 else 0
    state["LED3"] = 1 if buttons["PB3"] == 1 else 0
    state["LED4"] = 1 if buttons["PB4"] == 1 else 0
    state["BUZZ1"] = 1 if buttons["PB5"] == 1 else 0
    state["LED6"] = 1 if buttons["PB6"] == 1 else 0
    state["LED7"] = 1 if buttons["PB7"] == 1 else 0
    # state["LED8"] = 1 if buttons["PB8"] == 1 else 0
    # state["LED9"] = 1 if buttons["PB9"] == 1 else 0
    state["BUZZ2"] = 1 if buttons["PB8"] == 1 else 0

    return state
