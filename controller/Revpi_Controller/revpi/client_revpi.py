# ============================== # IMPORT LIBRARY # ============================== #
import asyncio
import json
import time

import websockets

from revpi.input_manager import (
    update_dashboard_input,
)

from revpi.data_provider import (
    read_all,
    get_actuator_state,
    get_control_mode,
    apply_control_command,
)

from revpi.logging import (
    measurements,
    event,
    ack,
)

# ============================== # CONTROLLER CONFIG # ============================== #
# NOTE: sebelumnya nilai ini hard-coded "revpi01" dan TIDAK PERNAH
# diganti oleh argumen --id di main.py (argumen --id dibaca tapi tidak
# pernah dikirim ke run_client()). Akibatnya, controller SELALU
# mendaftar ke gateway dengan id "revpi01" apapun --id yang diberikan
# di command line. Kalau dashboard/web client mengirim command dengan
# "target" != "revpi01", command itu tidak akan pernah sampai ke
# controller ini (gateway akan bilang "Controller not found").
#
# FIX: CONTROLLER_ID sekarang di-set lewat set_controller_id() yang
# dipanggil dari main.py sebelum run_client() dijalankan.
CONTROLLER_ID = "revpi01"


def set_controller_id(controller_id: str):
    """Dipanggil dari main.py agar --id benar-benar dipakai."""
    global CONTROLLER_ID
    CONTROLLER_ID = controller_id

# ============================== # BUILD TELEMETRY PAYLOAD # ============================== #
async def build_payload(loop):

    sensor_data = await loop.run_in_executor(
        None,
        read_all,
    )

    return {
        "type": "data",
        "source": CONTROLLER_ID,
        "telemetry_ts": time.time(),
        "MODE": get_control_mode(),
        #"SCENARIO": get_current_scenario(),
        "TEMP": sensor_data.get("TEMP", 0),
        "HUM": sensor_data.get("HUM", 0),
        "ANALOG": sensor_data.get("ANALOG", 0),
        "RTD": sensor_data.get("RTD", 0),
    }


# ============================== # SEND TELEMETRY DATA # ============================== #
async def send_data(ws):

    loop = asyncio.get_running_loop()

    while True:

        try:

            payload = await build_payload(loop)

            await ws.send(
                json.dumps(payload)
            )

            measurements(payload)

            print(
                "[SEND DATA]",
                payload,
            )

            await asyncio.sleep(1)

        except websockets.exceptions.ConnectionClosed:

            print("[SEND] WS disconnected")
            break


# ============================== # SEND OUTPUT INDICATOR # ============================== #
async def send_indicator(ws):

    loop = asyncio.get_running_loop()

    last_state = None

    while True:

        try:

            actuator_state = await loop.run_in_executor(
                None,
                get_actuator_state,
            )

            # Tidak berubah → tidak perlu kirim
            if actuator_state == last_state:
                await asyncio.sleep(0.05)
                continue

            last_state = actuator_state.copy()

            payload = {
                "type": "indicator",
                "source": CONTROLLER_ID,
                "telemetry_ts": time.time(),
                "MODE": get_control_mode(),
                **{
                    key: bool(value)
                    for key, value in actuator_state.items()
                },
            }

            await ws.send(json.dumps(payload))

            print("[SEND INDICATOR]", payload)

            await asyncio.sleep(0.05)

        except websockets.exceptions.ConnectionClosed:

            print("[INDICATOR] WS disconnected")
            break

# ============================== #
# RECEIVE CONTROL COMMAND
# ============================== #
async def receive_data(ws):

    loop = asyncio.get_running_loop()

    async for msg in ws:

        try:

            data = json.loads(msg)

            print("[RECV]", data)

            if data.get("type") != "command":
                continue

            command_id = data.get("command_id")
            payload = data.get("payload", {})

            if not payload:
                print("[COMMAND] Empty payload")
                continue

            start = time.perf_counter()

            # ==========================
            # Split Payload
            # ==========================

            input_payload = {}
            output_payload = {}

            for key, value in payload.items():

                if key.startswith(("PB", "SW", "EM", "PROXIMITY")):
                    input_payload[key] = value

                elif key.startswith(("LED", "BUZZ", "RELAY")):
                    output_payload[key] = value

            # ==========================
            # Virtual Input
            # ==========================

            if input_payload:

                update_dashboard_input(input_payload)

                print(
                    "[INPUT]",
                    input_payload,
                )

            # ==========================
            # Output Command
            # ==========================

            if output_payload:

                result = await loop.run_in_executor(
                    None,
                    apply_control_command,
                    output_payload,
                    command_id,
                )

                print(
                    "[OUTPUT]",
                    output_payload,
                )

            else:

                result = {
                    "success": True,
                    "error": None,
                }

            elapsed = (
                time.perf_counter() - start
            ) * 1000

            # ==========================
            # Logging
            # ==========================

            for key, value in payload.items():

                event(
                    command_id=command_id,
                    actuator=key,
                    status=str(value),
                    exec_time_ms=0,
                    success=result["success"],
                )

            ack_payload = {

                "type": "ack",
                "source": CONTROLLER_ID,
                "command_id": command_id,
                "MODE": get_control_mode(),
                "status": (
                    "ok"
                    if result["success"]
                    else (result.get("error") or "failed")
                ),
                "latency_ms": round(
                    elapsed,
                    2,
                ),
            }

            await ws.send(
                json.dumps(ack_payload)
            )

            ack(
                command_id=command_id,
                source=CONTROLLER_ID,
                status=ack_payload["status"],
                latency_ms=elapsed,
            )

            print(
                "[SEND ACK]",
                ack_payload,
            )

        except Exception as e:

            print(
                "[RECV ERROR]",
                e,
            )

# ============================== # RUN CLIENT WORKER # ============================== #
async def run_client(
    host,
    port,
):

    uri = f"ws://{host}:{port}"

    async with websockets.connect(
        uri,
        ping_interval=20,
        ping_timeout=20,
    ) as ws:

        print("[WS] Connected")

        handshake = {
            "role": "controller",
            "id": CONTROLLER_ID,
        }

        await ws.send(
            json.dumps(handshake)
        )

        print(
            "[HANDSHAKE SENT]",
            handshake,
        )

        send_task = asyncio.create_task(
            send_data(ws)
        )

        indicator_task = asyncio.create_task(
            send_indicator(ws)
        )

        recv_task = asyncio.create_task(
            receive_data(ws)
        )

        done, pending = await asyncio.wait(
            [
                send_task,
                indicator_task,
                recv_task
            ],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        await asyncio.gather(
            *pending,
            return_exceptions=True,
        )