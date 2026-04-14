# ============================== # IMPORT LIBRARY # ==============================
import argparse
import asyncio
import logging

from client_revpi import run_client
from logging import init_db, init_csv
from test_cases.mini_process_case import run_mini_process

logger = logging.getLogger("main_process")


# ============================== # ASYNC MAIN RUNTIME # ==============================
async def async_main(host: str, port: int, controller_id: str):
    init_db()
    init_csv()
    logger.info("Mini process control initialized")

    sensor_sample = {
        "TEMP": 36,
        "HUM": 75
    }

    result = run_mini_process(sensor_sample)
    logger.info("Mini process result: %s", result)

    while True:
        try:
            await run_client(host, port, controller_id)
        except Exception as e:
            logger.exception("Mini process disconnected: %s", e)

        await asyncio.sleep(3)


# ============================== # MAIN ENTRY # ==============================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--id", default="C1")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    asyncio.run(async_main(args.host, args.port, args.id))


# ============================== # RUN PROGRAM # ==============================
if __name__ == "__main__":
    main()