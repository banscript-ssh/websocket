# ============================== # IMPORT LIBRARY # ==============================
import asyncio
import json
import logging

from revpi.data_provider import (
    read_all,
    get_actuator_state,
    apply_local_control,
    get_control_mode,
)
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
            # ========================= # READ CURRENT MODE # ========================= #
            mode = get_control_mode()
            
            # ========================= # READ SENSOR DATA # =========================
            sensor_data = read_all()
            logger.debug("[MONITOR] Sensor data read: %s", sensor_data)
            print("[SENSOR]", sensor_data)

            # ========================= # LOCAL CONTROL # ========================= #
            local_result = apply_local_control()

            logger.debug(
                "[MONITOR] Local control executed (mode=%s)",
                mode
            )

            # ========================= # LOCAL RESULT DEBUG # ========================= #
            if local_result is not None:

                logger.debug(
                    "[MONITOR] Local state: %s",
                    local_result
                )

            # ========================= # READ ACTUATOR STATE # =========================
            actuator_state = get_actuator_state()
            logger.debug("[MONITOR] Actuator state: %s", actuator_state)
            print("[ACTUATOR]", actuator_state)

            # ========================= # FILTER LED STATUS FOR UI # =========================
            output_status = {
                k: bool(v)
                for k, v in actuator_state.items()
                if k.startswith(("LED","BUZZ","RELAY"))
            }
            logger.debug("[MONITOR] Output status (UI): %s", output_status)
            print("[OUTPUT_STATUS]", output_status)

            # ========================= # LOG LOCAL (CSV + DB) # =========================
            measurements({
                **sensor_data,
                **actuator_state
            })
            logger.debug("[MONITOR] Measurements logged to CSV/DB")

            # ========================= # BUILD PAYLOAD FOR GWEB # =========================
            payload = {
                "type": "indicator",

                "MODE": mode,

                **output_status,

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
            logger.info("[MONITOR] Payload sent (mode=%s)", mode)

        except Exception as e:
            logger.exception("[MONITOR] Monitoring error: %s", e)

        await asyncio.sleep(interval)
