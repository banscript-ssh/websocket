# ============================== # IMPORT LIBRARY # ==============================
import argparse
import asyncio
import logging

from app.server import WebsocketServer
from revpi.monitor import monitoring_task
from revpi.logging import init_db, init_csv   

logger = logging.getLogger("main")

async def async_main(host: str, port: int):
    init_db()
    init_csv()
    logger.info("Logger initialized (DB & CSV ready)")

    server = WebsocketServer(host, port)
    await server.start()
    logger.info("RevPi WebSocket Server running on %s:%d", host, port)

    # 🔑 START monitoring as background task
    asyncio.create_task(
        monitoring_task(server, interval=1.0)
    )

    # 🔑 KEEP EVENT LOOP ALIVE
    await asyncio.Event().wait()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--log", default="info")
    args = parser.parse_args()

    level = getattr(logging, args.log.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    try:
        asyncio.run(async_main(args.host, args.port))
    except KeyboardInterrupt:
        logger.info("Shutting down RevPi server...")


if __name__ == "__main__":
    main()
