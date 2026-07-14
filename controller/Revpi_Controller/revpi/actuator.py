def control_actuators(buttons):
    """
    Digital Input -> Digital Output Mapping (I/O Testing)
    """

    state = {
        "BUZZ1": 0,
        "BUZZ2": 0,
        "BUZZ3": 0,
        "LED1": 0,
        "LED2": 0,
        "LED3": 0,
        "LED4": 0,
        "LED5": 0,
        "LED6": 0,
        "LED7": 0,
        "LED8": 0,
        "RELAY_MOTOR": 0,
        "RELAY_FAN": 0,
        "RELAY_LAMP": 0,
    }

    # =========================
    # PUSH BUTTON
    # =========================
    state["BUZZ1"] = int(buttons["PB1"]) # Assuming PB1 controls the BUZZ1
    state["BUZZ2"] = int(buttons["PB2"]) # Assuming PB2 controls the BUZZ2
    state["BUZZ3"] = int(buttons["PB3"]) # Assuming PB3 controls the BUZZ3

    state["LED1"] = int(buttons["PB4"]) # Assuming PB4 controls the LED1
    state["LED2"] = int(buttons["PB5"]) # Assuming PB5 controls the LED2
    state["LED3"] = int(buttons["PB6"]) # Assuming PB6 controls the LED3
    state["LED4"] = int(buttons["PB7"]) # Assuming PB7 controls the LED4
    state["LED5"] = int(buttons["PB8"]) # Assuming PB8 controls the LED5

    # =========================
    # EMERGENCY & SELECTOR
    # =========================
    state["LED6"] = int(buttons["EM9"]) # Assuming EM9 controls the LED6
    state["LED7"] = int(buttons["SW10"]) # Assuming SW10 controls the LED7
    state["LED8"] = int(buttons["SW11"]) # Assuming SW11 controls the LED8
    state["RELAY_MOTOR"] = int(buttons["SW12"]) # Assuming SW12 controls the RELAY_MOTOR
    state["RELAY_FAN"] = int(buttons["SW13"]) # Assuming SW13 controls the RELAY_FAN
    state["RELAY_LAMP"] = int(buttons["SW14"])  # Assuming SW14 controls the RELAY_LAMP
    
    return state