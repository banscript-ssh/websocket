# ============================== # IMPORT LIBRARY # ============================== #
import asyncio
import json
import logging
import socket

logger = logging.getLogger("app/discovery")

# ============================== # CONFIG # ============================== #
BEACON_PORT = 9999
BEACON_INTERVAL = 2

# ============================== # BROADCAST BEACON # ============================== #
async def broadcast_beacon(gateway_port: int):
    """
    Mengirim UDP broadcast berisi info gateway (port) ke seluruh jaringan
    lokal, supaya controller bisa menemukan IP gateway secara otomatis
    walau IP gateway berubah-ubah (DHCP).
    """

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM,
        socket.IPPROTO_UDP,
    )

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    message = json.dumps({
        "service": "revpi_gateway",
        "port": gateway_port,
    }).encode()

    logger.info(
        "[DISCOVERY] Broadcasting beacon on UDP port %d every %ds",
        BEACON_PORT,
        BEACON_INTERVAL,
    )

    try:
        while True:

            try:
                sock.sendto(
                    message,
                    ("255.255.255.255", BEACON_PORT),
                )

            except Exception:
                logger.exception("[DISCOVERY] Failed to send beacon")

            await asyncio.sleep(BEACON_INTERVAL)

    finally:
        sock.close()
