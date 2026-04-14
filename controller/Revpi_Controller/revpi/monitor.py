# ============================== # IMPORT LIBRARY # ==============================
import asyncio
import json
import logging

from revpi.data_provider import read_all, get_actuator_state, process_actuators
from revpi.logging import measurements  

logger = logging.getLogger("revpi/monitoring")

# ============================== # CREATE TASK MONITORING # ==============================
async def monitoring_task(server, interval: float = 1.0):
    """
    Periodically read sensor & actuator data from RevPi,
    log it locally, and broadcast it to all connected WebSocket clients.
    """

    logger.info("Monitoring task started (interval=%ss)", interval)

    while True:
        try:
            # ========================= # READ SENSOR DATA # =========================
            sensor_data = read_all()
            logger.debug("[MONITOR] Sensor data read: %s", sensor_data)
            print("[SENSOR]", sensor_data)

            # ========================= # PROCESS ACTUATORS # =========================
            process_actuators()
            logger.debug("[MONITOR] Actuators processed")

            # ========================= # READ ACTUATOR STATE # =========================
            actuator_state = get_actuator_state()
            logger.debug("[MONITOR] Actuator state: %s", actuator_state)
            print("[ACTUATOR]", actuator_state)

            # ========================= # FILTER LED STATUS FOR UI # =========================
            led_status = {
                k: bool(v)
                for k, v in actuator_state.items()
                if k.startswith(("LED","BUZZ"))
            }
            logger.debug("[MONITOR] LED status (UI): %s", led_status)
            print("[LED_STATUS]", led_status)

            # ========================= # LOG LOCAL (CSV + DB) # =========================
            measurements({
                **sensor_data,
                **actuator_state
            })
            logger.debug("[MONITOR] Measurements logged to CSV/DB")

            # ========================= # BUILD PAYLOAD FOR GWEB # =========================
            payload = {
                "type": "indicator",
                **led_status,
                "TEMP": sensor_data.get("TEMP", 0),
                "HUM": sensor_data.get("HUM", 0),
                "RTD": sensor_data.get("RTD", 0),
                "ANALOG": sensor_data.get("ANALOG", 0),
            }

            message = json.dumps(payload)
            logger.debug("[MONITOR] Payload to GWeb: %s", payload)
            print("[SEND TO GWEB]", payload)

            # ========================= # SEND TO GWEB # =========================
            await server.broadcast(message)
            logger.info("[MONITOR] Payload sent to GWeb")

        except Exception as e:
            logger.exception("[MONITOR] Monitoring error: %s", e)

        await asyncio.sleep(interval)
