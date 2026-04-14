# ============================== # IMPORT LIBRARY # ==============================
import websockets
import asyncio
import json
import time

from data_provider import read_all, process_actuators, get_actuator_state
from logging import measurements, event, ack


# ============================== # BUILD TELEMETRY PAYLOAD # ==============================
async def build_payload(loop, controller_id, command_id=None):
    sensor_data = await loop.run_in_executor(None, read_all)
    actuator_state = await loop.run_in_executor(None, get_actuator_state)

    led_status = {
        k: bool(v)
        for k, v in actuator_state.items()
        if k.startswith("LED") or k.startswith("BUZZ")
    }

    payload = {
        "type": "data",
        "source": controller_id,
        "telemetry_ts": time.time(),
        **led_status,
        "TEMP": sensor_data.get("TEMP", 0),
        "HUM": sensor_data.get("HUM", 0),
        "ANALOG": sensor_data.get("ANALOG", 0),
        "RTD": sensor_data.get("RTD", 0)
    }

    if command_id:
        payload["command_id"] = command_id

    return payload


# ============================== # SEND DATA (PERIODIC MONITORING) # ==============================
async def send_data(ws, controller_id):
    loop = asyncio.get_running_loop()

    while True:
        try:
            payload = await build_payload(loop, controller_id)

            await ws.send(json.dumps(payload))
            measurements(payload)

            print("[SEND DATA]", payload)

            await asyncio.sleep(1)

        except websockets.exceptions.ConnectionClosed:
            print("[SEND] WS disconnected")
            break


# ============================== # SEND EVENT TELEMETRY # ==============================
async def send_event_data(ws, controller_id, command_id):
    loop = asyncio.get_running_loop()
    payload = await build_payload(loop, controller_id, command_id)

    await ws.send(json.dumps(payload))
    measurements(payload)

    print("[SEND EVENT DATA]", payload)


# ============================== # RECEIVE DATA (CONTROL) # ==============================
async def receive_data(ws, controller_id):
    loop = asyncio.get_running_loop()

    async for msg in ws:
        try:
            data = json.loads(msg)
            print("[RECV]", data)

            if data.get("type") == "command":
                t_start = time.time()

                await loop.run_in_executor(None, process_actuators, data)

                exec_time_ms = (time.time() - t_start) * 1000

                for key, value in data.items():
                    if key.startswith("LED") or key.startswith("BUZZ"):
                        event(
                            command_id=data.get("command_id"),
                            actuator=key,
                            status=str(value),
                            exec_time_ms=exec_time_ms,
                            success=True
                        )

                ack_payload = {
                    "type": "ack",
                    "source": controller_id,
                    "command_id": data.get("command_id"),
                    "status": "ok",
                    "latency_ms": exec_time_ms
                }

                await ws.send(json.dumps(ack_payload))

                ack(
                    command_id=data.get("command_id"),
                    source=controller_id,
                    status="ok",
                    latency_ms=exec_time_ms
                )

                print("[SEND ACK]", ack_payload)

                await send_event_data(
                    ws,
                    controller_id,
                    data.get("command_id")
                )

        except Exception as e:
            print("[RECV ERROR]", e)


# ============================== # RUN CLIENT WORKER # ==============================
async def run_client(host, port, controller_id):
    uri = f"ws://{host}:{port}"

    async with websockets.connect(uri) as ws:
        print("[WS] Connected")

        handshake = {
            "role": "controller",
            "id": controller_id
        }

        await ws.send(json.dumps(handshake))
        print("[HANDSHAKE SENT]", handshake)

        send_task = asyncio.create_task(send_data(ws, controller_id))
        recv_task = asyncio.create_task(receive_data(ws, controller_id))

        done, pending = await asyncio.wait(
            [send_task, recv_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()