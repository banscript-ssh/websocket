import websockets
import argparse
import asyncio
import json
import random

async def receive_data(websocket):
    while True:
        try:
            server_msg = await websocket.recv()
            print(f"[RECV] {server_msg}")
        except websockets.exceptions.ConnectionClosed:
            print("[RECV] Connection closed by server.")
            break
        except Exception as e:
            print(f"[RECV] Error: {e}")
            break

async def send_data(websocket):
    while True:
        # dummy_data = {
        #        "type": "indicator",
        #         "LED1": False,
        #         "LED2": True,
        #         "LED3": False,
        #         "LED4": True,
        #         "LED5": True,
        #         "LED6": False,
        #         "LED7": True,
        #         "LED8": True,
        #         "BUZZ1": False,
        #         "BUZZ2": True,
        #         "TEMP": round(random.uniform(20.0, 32.0), 2),
        #         "HUM": round(random.uniform(0.0, 100.0), 2),
        #         "ANALOG": round(random.uniform(4.0, 20.0), 2),
        #         "RTD": round(random.uniform(0.0, 100.0), 2)
            }
        await websocket.send(json.dumps(dummy_data))
        print(f"[SEND] {dummy_data}")
        await asyncio.sleep(1)

async def run_client(host: str, port: int):
    uri = f"ws://{host}:{port}"
    async with websockets.connect(uri) as websocket:
        await asyncio.gather(
            receive_data(websocket),
            send_data(websocket)
        )

def client():
    parser = argparse.ArgumentParser(description="Test WebSocket Client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    try:
        asyncio.run(run_client(args.host, args.port))
    except KeyboardInterrupt:
        print("\n[EXIT] Client stopped by user")

if __name__ == "__main__":
    client()
