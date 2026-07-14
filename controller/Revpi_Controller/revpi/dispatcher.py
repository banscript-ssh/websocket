import asyncio
import logging

from scenarios import (
    io_test_case,
    logic_gate_case,
    traffic_light_case,
    mini_process_case,
    conveyor_counter_case
)

logger = logging.getLogger("dispatcher")

SCENARIOS = {
    "io": io_test_case,
    "logic": logic_gate_case,
    "traffic": traffic_light_case,
    "process": mini_process_case,
    "conveyor": conveyor_counter_case
}


async def run_dispatcher(
    mode: str,
    cycle_time: float = 0.1
):

    if mode not in SCENARIOS:

        raise ValueError(
            f"Unknown Scenario : {mode}"
        )

    scenario = SCENARIOS[mode]

    logger.info("=" * 50)
    logger.info("Selected Scenario : %s", mode.upper())
    logger.info("=" * 50)

    await scenario.initialize()

    logger.info("Scenario Started")

    try:

        while True:

            try:

                await scenario.update()

            except Exception:

                logger.exception(
                    "Scenario Update Error"
                )

            await asyncio.sleep(cycle_time)

    finally:

        logger.info("Stopping Scenario...")

        await scenario.shutdown()

        logger.info("Scenario Shutdown Complete")