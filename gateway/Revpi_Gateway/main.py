# ============================== # IMPORT LIBRARY # ============================== #
import asyncio
import time
from app.server import WebsocketServer


# ============================== # MAIN ENTRY # ================================== #
async def main():
    server = WebsocketServer(host="0.0.0.0", port=8765)
    await server.start()

    print("[GATEWAY] Server running on ws://0.0.0.0:8765")
    print(f"[GATEWAY] Startup timestamp: {time.time()}")

    # Optional monitoring task
    heartbeat_task = asyncio.create_task(server.monitor_clients())

    try:
        while True:
            await asyncio.sleep(3600)

    finally:
        print("[GATEWAY] Stopping server...")
        heartbeat_task.cancel()
        await server.stop()

# ============================== # RUN # ========================================== #
if __name__ == "__main__":
    asyncio.run(main())