import asyncio
import websockets

async def test():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as ws:
        await ws.send('{"join":"revpi"}')
        print("Connected!")

        while True:
            await ws.send('{"type":"heartbeat"}')
            await asyncio.sleep(2)

asyncio.run(test())