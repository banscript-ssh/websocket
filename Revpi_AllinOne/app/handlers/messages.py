import json
import logging
from typing import Optional
import uuid
from utils.csv_logger import log_receive_command
import websockets

logger = logging.getLogger("app/handlers/message")

async def handle_message(
    websocket: websockets.WebSocketServerProtocol,
    message: str,
    server,   # 🔥 sekarang pakai server, bukan clients
    peer: Optional[tuple]
):
    logger.info("Received message from %s: %s", peer, message)

    # ===================== PARSE JSON =====================
    try:
        data = json.loads(message)
    except Exception:
        logger.warning("Invalid JSON from %s", peer)
        return

    msg_type = data.get("type")

    # =====================================================
    # 🔥 COMMAND FLOW (WEB → CONTROLLER)
    # =====================================================
    if msg_type == "command":
        command_id = f"cmd-{uuid.uuid4()}"

        target = data.get("target")
        if not target:
            logger.warning("Command tanpa target dari %s", peer)
            return

        controller_ws = server.controllers.get(target)
        if not controller_ws:
            logger.warning("Controller %s tidak ditemukan", target)
            return

        # ====== LOG COMMAND ======
        source_ip = peer[0] if peer else "unknown"
        source_port = peer[1] if peer else -1

        log_receive_command(
            command_id=command_id,
            source_ip=source_ip,
            source_port=source_port,
            parsed_keys=data.keys(),
            raw_payload=message,
        )

        # ====== FORWARD KE CONTROLLER ======
        data["command_id"] = command_id

        try:
            await controller_ws.send(json.dumps(data))
            logger.info("Command forwarded to controller %s", target)
        except Exception as e:
            logger.error("Failed to send to controller %s: %s", target, e)

    # =====================================================
    # 🔥 DATA FLOW (CONTROLLER → WEB)
    # =====================================================
    elif msg_type == "data":
        try:
            await server.broadcast_to_web(message)
            logger.info("Data broadcasted to web clients")
        except Exception as e:
            logger.error("Broadcast error: %s", e)

    # =====================================================
    # 🔥 ACK / RESPONSE (OPTIONAL)
    # =====================================================
    elif msg_type == "ack":
        try:
            await server.broadcast_to_web(message)
        except Exception:
            pass

    # =====================================================
    # UNKNOWN TYPE
    # =====================================================
    else:
        logger.warning("Unknown message type from %s: %s", peer, msg_type)