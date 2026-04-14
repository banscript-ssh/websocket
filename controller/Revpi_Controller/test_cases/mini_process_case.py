# ============================== # MINI PROCESS CONTROL CASE # ==============================
def run_mini_process(sensor_data: dict):
    temp = sensor_data.get("TEMP", 0)
    hum = sensor_data.get("HUM", 0)

    command = {}

    # suhu tinggi → buzzer + LED merah
    if temp > 35:
        command["LED7"] = 1
        command["BUZZ1"] = 1
    else:
        command["LED7"] = 0
        command["BUZZ1"] = 0

    # humidity tinggi → LED warning tambahan
    if hum > 70:
        command["LED6"] = 1
    else:
        command["LED6"] = 0

    return command