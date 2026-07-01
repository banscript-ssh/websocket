# ============================== #
# IMPORT LIBRARY
# ============================== #

import json
import logging
import time
from typing import Optional

import websockets

from utils.csv_logger import (
    log_receive_command,
    log_ack,
    log_data,
    log_telemetry_interval,
)

logger = logging.getLogger("app/handlers/message")


# ============================== #
# HANDLE MESSAGE
# ============================== #

async def handle_message(
    websocket: websockets.WebSocketServerProtocol,
    message: str,
    server,
    peer: Optional[tuple]
):

    logger.info("Received message from %s", peer)

    # ==========================================================
    # PARSE JSON
    # ==========================================================

    try:
        data = json.loads(message)

    except json.JSONDecodeError:

        logger.warning("Invalid JSON from %s", peer)
        return

    # ==========================================================
    # DETECT MESSAGE SOURCE
    # ==========================================================

    if websocket in server.web_clients:

        logger.info("[SOURCE] WEB CLIENT")

        # Dashboard hanya mengirim state I/O,
        # Gateway membungkus menjadi command.

        data = {
            "type": "command",
            "target": "revpi01",       # <-- Sesuaikan dengan ID Controller
            "payload": data
        }

        msg_type = "command"

    elif websocket in server.controllers.values():

        logger.info("[SOURCE] CONTROLLER")

        msg_type = data.get("type")

    else:

        logger.warning(
            "Unknown websocket source : %s",
            peer
        )
        return

    logger.info("[MESSAGE] Type : %s", msg_type)

    # ==========================================================
    # COMMAND FLOW
    # WEB  ---> CONTROLLER
    # ==========================================================

    if msg_type == "command":

        command_id = server.generate_correlation_id()

        target = data.get("target")

        if not target:

            logger.warning(
                "Command tanpa target dari %s",
                peer
            )
            return

        controller_ws = server.controllers.get(target)

        if not controller_ws:

            logger.warning(
                "Controller %s tidak ditemukan",
                target
            )

            error_payload = {
                "type": "ack",
                "command_id": command_id,
                "status": "controller_not_found"
            }

            await server.forward_ack_to_web(
                json.dumps(error_payload)
            )

            return

        source_ip = peer[0] if peer else "unknown"
        source_port = peer[1] if peer else -1

        # ======================================================
        # CSV LOGGER
        # ======================================================

        log_receive_command(
            command_id=command_id,
            source_ip=source_ip,
            source_port=source_port,
            parsed_keys=data["payload"].keys(),
            raw_payload=message,
        )

        # ======================================================
        # ADD METADATA
        # ======================================================

        data["command_id"] = command_id
        data["gateway_ts"] = time.time()

        logger.info(
            "\n========== TX TO CONTROLLER ==========\n"
            "Target : %s\n"
            "%s\n"
            "=====================================",
            target,
            json.dumps(data, indent=4)
        )

        try:

            await server.send_to_controller(
                target,
                json.dumps(data)
            )

            logger.info(
                "[COMMAND] Forwarded | CMD=%s | Target=%s",
                command_id,
                target
            )

        except Exception as e:

            logger.error(
                "Failed sending command to %s : %s",
                target,
                e
            )

    # ==========================================================
    # TELEMETRY FLOW
    # CONTROLLER ---> WEB
    # ==========================================================

    elif msg_type == "data":

        logger.info(
            "\n========== RX TELEMETRY ==========\n%s\n"
            "==================================",
            json.dumps(data, indent=4)
        )

        logger.info(
            "[DATA] Source=%s | TEMP=%s | HUM=%s",
            data.get("source"),
            data.get("TEMP"),
            data.get("HUM"),
        )

        try:

            log_data(data)

            log_telemetry_interval()

            await server.broadcast_to_web(message)

            logger.info(
                "[DATA] Broadcast to Web Client Success"
            )

        except Exception as e:

            logger.error(
                "Broadcast error : %s",
                e
            )

    # ==========================================================
    # ACK FLOW
    # CONTROLLER ---> WEB
    # ==========================================================

    elif msg_type == "ack":

        logger.info(
            "\n========== RX ACK ==========\n%s\n"
            "============================",
            json.dumps(data, indent=4)
        )

        logger.info(
            "[ACK] CMD=%s | STATUS=%s",
            data.get("command_id"),
            data.get("status"),
        )

        try:

            log_ack(
                command_id=data.get("command_id"),
                source=data.get("source"),
                status=data.get("status"),
                latency_ms=data.get("latency_ms"),
            )

            await server.forward_ack_to_web(message)

            logger.info(
                "[ACK] Forwarded to Web Client"
            )

        except Exception as e:

            logger.error(
                "ACK handling error : %s",
                e
            )

    # ==========================================================
    # UNKNOWN MESSAGE
    # ==========================================================

    else:

        logger.warning(
            "Unknown message type from %s : %s",
            peer,
            msg_type
        )