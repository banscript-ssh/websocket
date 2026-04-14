# ============================== # IMPORT LIBRARY # ==============================
import argparse
import asyncio
import logging

from client_revpi import run_client
from logging import init_db, init_csv

logger = logging.getLogger("main")


# ============================== # ASYNC MAIN RUNTIME # ==============================
async def async_main(host: str, port: int, controller_id: str):
    init_db()
    init_csv()
    logger.info("Controller logger initialized")

    while True:
        try:
            await run_client(host, port, controller_id)

        except Exception as e:
            logger.exception("Controller disconnected: %s", e)

        logger.warning("Reconnect in 3 seconds...")
        await asyncio.sleep(3)


# ============================== # MAIN ENTRY # ==============================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--id", default="C1")
    parser.add_argument("--log", default="info")
    args = parser.parse_args()

    level = getattr(logging, args.log.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    try:
        asyncio.run(
            async_main(args.host, args.port, args.id)
        )
    except KeyboardInterrupt:
        logger.info("Shutting down RevPi controller...")


# ============================== # RUN PROGRAM # ==============================
if __name__ == "__main__":
    main()