# ============================== # IMPORT LIBRARY # ============================== #
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

# ============================== # HANDLE MESSAGE # ============================== #
async def handle_message(
    websocket: websockets.WebSocketServerProtocol,
    message: str,
    server,
    peer: Optional[tuple]
):
    logger.info("Received message from %s: %s", peer, message)

    # ===================== PARSE JSON ===================== #
    try:
        data = json.loads(message)
    except Exception:
        logger.warning("Invalid JSON from %s", peer)
        return
    msg_type = data.get("type")

    # ========================================================================== #
    # COMMAND FLOW (WEB → CONTROLLER)
    # ========================================================================== #
    if msg_type == "command":
        # ===================== GENERATE COMMAND ID ===================== #
        command_id = server.generate_correlation_id()
        # ===================== GET TARGET CONTROLLER ===================== #
        target = data.get("target")
        if not target:
            logger.warning("Command tanpa target dari %s", peer)
            return

        # ===================== CHECK CONTROLLER ===================== #
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

        # ===================== GET SOURCE INFORMATION ===================== #
        source_ip = peer[0] if peer else "unknown"
        source_port = peer[1] if peer else -1

        # ===================== CSV LOGGER ===================== #
        # Simpan command yang diterima gateway
        log_receive_command(
            command_id=command_id,
            source_ip=source_ip,
            source_port=source_port,
            parsed_keys=data.keys(),
            raw_payload=message,
        )

        # ===================== ADD METADATA ===================== #
        data["command_id"] = command_id
        data["gateway_ts"] = time.time()

        # ===================== FORWARD COMMAND ===================== #
        try:
            await server.send_to_controller(
                target,
                json.dumps(data)
            )

            logger.info(
                "[COMMAND] forwarded | cmd_id=%s | target=%s",
                command_id,
                target
            )
        except Exception as e:
            logger.error(
                "Failed to send to controller %s: %s",
                target,
                e
            )

    # ========================================================================== #
    # DATA FLOW (CONTROLLER → WEB)
    # ========================================================================== #
    elif msg_type == "data":
        try:
            logger.info(
                "[DATA] source=%s TEMP=%s HUM=%s",
                data.get("source"),
                data.get("TEMP"),
                data.get("HUM"),
            )

            # ===================== CSV LOGGER ===================== #
            # Simpan data telemetry sensor
            log_data(data)

            # Hitung interval antar paket telemetry
            log_telemetry_interval()

            # ===================== BROADCAST DATA ===================== #
            await server.broadcast_to_web(message)
        except Exception as e:
            logger.error(
                "Broadcast error: %s",
                e
            )

    # ========================================================================== #
    # ACK / RESPONSE FLOW (CONTROLLER → WEB)
    # ========================================================================== #
    elif msg_type == "ack":
        try:
            logger.info(
                "[ACK] cmd_id=%s | source=%s | status=%s",
                data.get("command_id"),
                data.get("source"),
                data.get("status"),
            )

            # ===================== CSV LOGGER ===================== #
            # Simpan acknowledgement dari controller
            log_ack(
                command_id=data.get("command_id"),
                source=data.get("source"),
                status=data.get("status"),
                latency_ms=data.get("latency_ms"),
            )
            # ===================== FORWARD ACK ===================== #
            await server.forward_ack_to_web(message)
        except Exception as e:
            logger.error(
                "ACK handling error: %s",
                e
            )

    # ========================================================================== #
    # UNKNOWN TYPE
    # ========================================================================== #
    else:
        logger.warning(
            "Unknown message type from %s: %s",
            peer,
            msg_type
        )