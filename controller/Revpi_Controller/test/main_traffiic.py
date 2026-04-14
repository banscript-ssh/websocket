# ============================== # IMPORT LIBRARY # ==============================
import argparse
import asyncio
import logging

from client_revpi import run_client
from logging import init_db, init_csv
from test_cases.traffic_light_case import run_traffic_cycle

logger = logging.getLogger("main_traffic")


# ============================== # ASYNC MAIN RUNTIME # ==============================
async def async_main(host: str, port: int, controller_id: str):
    init_db()
    init_csv()
    logger.info("Traffic light case initialized")

    traffic_task = asyncio.create_task(run_traffic_cycle())
    client_task = asyncio.create_task(run_client(host, port, controller_id))

    await asyncio.gather(traffic_task, client_task)


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