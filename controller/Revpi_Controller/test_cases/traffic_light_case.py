# ============================== # IMPORT LIBRARY # ==============================
import asyncio

# ============================== # TRAFFIC LIGHT CASE # ==============================
async def run_traffic_cycle(process_actuators):
    sequence = [
        {"LED1": 1, "LED2": 0, "LED3": 0},  # merah
        {"LED1": 0, "LED2": 1, "LED3": 0},  # kuning
        {"LED1": 0, "LED2": 0, "LED3": 1},  # hijau
    ]

    while True:
        for state in sequence:
            process_actuators(state)
            await asyncio.sleep(1)