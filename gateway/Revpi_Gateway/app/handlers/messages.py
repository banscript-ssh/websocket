# ============================== # IMPORT LIBRARY # ============================== #
import json
import logging
import time
import websockets

from typing import Optional
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

    logger.info(
        "Received message from %s",
        peer
    )

    # ============================== # PARSE JSON # ============================== #
    try:
        data = json.loads(message)

    except json.JSONDecodeError:
        logger.warning(
            "Invalid JSON from %s",
            peer
        )
        return

    # ============================== # IDENTIFY SOURCE # ============================== #
    if websocket in server.web_clients:

        logger.info("[SOURCE] WEB CLIENT")
        target = data.pop(
            "target",
            "revpi01"
        )

        data = {
            "type": "command",
            "target": target,
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

    logger.info(
        "[MESSAGE] Type : %s",
        msg_type
    )

    # ============================== # COMMAND FLOW # ============================== #
    if msg_type == "command":
        command_id = server.generate_correlation_id()
        target = data.get("target")

        if not target:
            logger.warning(
                "Command without target"
            )
            return

        if target not in server.controllers:
            logger.warning(
                "Controller %s not found",
                target
            )

            await server.forward_ack_to_web(
                json.dumps({
                    "type": "ack",
                    "command_id": command_id,
                    "status": "controller_not_found"
                })
            )
            return

        source_ip = peer[0] if peer else "unknown"
        source_port = peer[1] if peer else -1

        log_receive_command(
            command_id=command_id,
            source_ip=source_ip,
            source_port=source_port,
            parsed_keys=data["payload"].keys(),
            raw_payload=message,
        )

        data["command_id"] = command_id
        data["gateway_ts"] = time.time()

        logger.info(
            "[COMMAND] CMD=%s Target=%s",
            command_id,
            target
        )

        success = await server.send_to_controller(
            target,
            json.dumps(data)
        )

        if success:
            logger.info(
                "[COMMAND] Forward Success"
            )

        else:
            logger.warning(
                "[COMMAND] Forward Failed"
            )

    # ============================== # TELEMETRY FLOW # ============================== #
    elif msg_type == "data":
        logger.info(
            "[DATA] %s",
            data.get("source")
        )

        log_data(data, raw_payload=message)
        log_telemetry_interval()

        await server.broadcast_to_web(message)

    # ============================== # INDICATOR FLOW # ============================== #
    elif msg_type == "indicator":
        logger.info(
            "[INDICATOR] %s",
            data.get("source")
        )

        await server.broadcast_to_web(message) 

    # ============================== # ACK FLOW # ============================== #
    elif msg_type == "ack":
        logger.info(
            "[ACK] CMD=%s STATUS=%s",
            data.get("command_id"),
            data.get("status")
        )

        log_ack(
            command_id=data.get("command_id"),
            source=data.get("source"),
            status=data.get("status"),
            latency_ms=data.get("latency_ms"),
        )
        await server.forward_ack_to_web(message)

    # ============================== # UNKNOWN MESSAGE # ============================== #
    else:
        logger.warning(
            "Unknown message type : %s",
            msg_type
        )