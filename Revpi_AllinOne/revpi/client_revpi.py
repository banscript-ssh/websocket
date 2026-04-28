# ============================== # IMPORT LIBRARY # ==============================
import websockets
import argparse
import asyncio
import json

from data_provider import read_all, process_actuators, get_actuator_state

# =============================== # SEND DATA (MONITORING) # ===============================
async def send_data(ws, controller_id):
    loop = asyncio.get_running_loop()

    while True:
        try:
            sensor_data = await loop.run_in_executor(None, read_all)
            actuator_state = await loop.run_in_executor(None, get_actuator_state)

            led_status = {
                k: bool(v)
                for k, v in actuator_state.items()
                if k.startswith("LED")
            }

            payload = {
                "type": "data",  # 🔥 update
                "source": controller_id,
                **led_status,
                "TEMP": sensor_data.get("TEMP", 0),
                "HUM": sensor_data.get("HUM", 0),
                "ANALOG": sensor_data.get("ANALOG", 0),
                "RTD": sensor_data.get("RTD", 0)
            }

            await ws.send(json.dumps(payload))
            print("[SEND DATA]", payload)

            await asyncio.sleep(1)

        except websockets.exceptions.ConnectionClosed:
            print("[SEND] WS disconnected")
            break

# =============================== # RECEIVE DATA (CONTROL) # ===============================
async def receive_data(ws, controller_id):
    loop = asyncio.get_running_loop()

    async for msg in ws:
        try:
            data = json.loads(msg)
            print("[RECV]", data)

            # =====================
            # COMMAND HANDLER
            # =====================
            if data.get("type") == "command":
                await loop.run_in_executor(
                    None, process_actuators, data
                )

                # 🔥 KIRIM ACK
                ack = {
                    "type": "ack",
                    "source": controller_id,
                    "command_id": data.get("command_id"),
                    "status": "ok"
                }

                await ws.send(json.dumps(ack))
                print("[SEND ACK]", ack)

        except Exception as e:
            print("[RECV ERROR]", e)


# =============================== # RUN CLIENT # ===============================
async def run_client(host, port, controller_id):
    uri = f"ws://{host}:{port}"

    async with websockets.connect(uri) as ws:
        print("[WS] Connected")

        # =====================
        # 🔥 HANDSHAKE ROLE
        # =====================
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

# =============================== # CLI ENTRY # ===============================
def client():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--id", default="C1")  # 🔥 tambah ID controller
    args = parser.parse_args()

    asyncio.run(run_client(args.host, args.port, args.id))

if __name__ == "__main__":
    client()