# ============================== # IMPORT LIBRARY # ============================== #
import argparse
import asyncio
import logging
import time

from app.server import WebSocketGatewayServer
from app.discovery import broadcast_beacon

logger = logging.getLogger("main")

# ============================== # MAIN ENTRY # ================================== #
async def main(host: str, port: int):
    server = WebSocketGatewayServer(host=host, port=port)
    await server.start()

    print(f"[GATEWAY] Server running on ws://{host}:{port}")
    print(f"[GATEWAY] Startup timestamp: {time.time()}")

    # Monitoring task
    heartbeat_task = asyncio.create_task(server.monitor_clients())

    # Beacon task - biar controller bisa auto-discover IP gateway ini
    # walaupun IP-nya berubah-ubah (DHCP), tanpa perlu --host manual
    beacon_task = asyncio.create_task(broadcast_beacon(port))

    try:
        while True:
            await asyncio.sleep(3600)

    finally:
        print("[GATEWAY] Stopping server...")
        heartbeat_task.cancel()
        beacon_task.cancel()
        await server.stop()

# ============================== # RUN # ========================================== #
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--log", default="info")

    args = parser.parse_args()

    level = getattr(logging, args.log.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    asyncio.run(main(args.host, args.port))
