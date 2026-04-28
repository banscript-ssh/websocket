# ============================== # IMPORT LIBRARY # ==============================
import asyncio
import logging
import json
from typing import Optional
import websockets

from app.handlers.messages import handle_message

logger = logging.getLogger("app/server")


# ============================== # PARSING CLASS WebSocket Server # ==============================
class WebsocketServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.controllers: dict[str, websockets.WebSocketServerProtocol] = {}
        self.web_clients: set[websockets.WebSocketServerProtocol] = set()
        self.host = host
        self.port = port
        self._server: Optional[websockets.server.Serve] = None
        self._clients: set[websockets.WebSocketServerProtocol] = set()

    # ============================== # HANDLER CLIENT WEBSOCKET # ==============================
    async def handler(self, websocket: websockets.WebSocketServerProtocol):
        peer = websocket.remote_address
        logger.info("Client connected: %s", peer)

        self._clients.add(websocket)

        role = None
        client_id = None

        try:
            # ======================
            # HANDSHAKE ROLE
            # ======================
            init_msg = await websocket.recv()

            try:
                data = json.loads(init_msg)
            except Exception:
                logger.warning("Invalid handshake from %s", peer)
                return

            role = data.get("role")
            client_id = data.get("id")

            if role == "controller":
                if not client_id:
                    logger.warning("Controller tanpa ID: %s", peer)
                    return
                self.controllers[client_id] = websocket
                logger.info("Registered controller: %s", client_id)

            elif role == "web":
                self.web_clients.add(websocket)
                logger.info("Registered web client: %s", peer)

            else:
                logger.warning("Unknown role from %s", peer)
                return

            # ======================
            # MAIN LOOP
            # ======================
            async for message in websocket:
                await handle_message(
                    websocket,
                    message,
                    self,   # kirim server object
                    peer
                )

        except websockets.exceptions.ConnectionClosedOK:
            logger.info("Connection closed cleanly: %s", peer)

        except Exception:
            logger.exception("Connection error with %s", peer)

        finally:
            self._clients.discard(websocket)

            # ======================
            # CLEANUP ROLE
            # ======================
            if role == "controller" and client_id:
                self.controllers.pop(client_id, None)
                logger.info("Controller removed: %s", client_id)

            elif role == "web":
                self.web_clients.discard(websocket)

            logger.info("Client disconnected: %s", peer)

    # ============================== # HANDLER BROADCAST WEBSOCKET # ==============================
    async def broadcast_to_web(self, payload: str):
        dead = set()
        for ws in self.web_clients:
            try:
                await ws.send(payload)
            except Exception:
                dead.add(ws)
        self.web_clients -= dead

    async def start(self):
        logger.info("Starting websocket server on %s:%d", self.host, self.port)
        self._server = await websockets.serve(self.handler, self.host, self.port)

    async def stop(self):
        if self._server is None:
            return
        logger.info("Stopping websocket server")
        self._server.close()
        await self._server.wait_closed()

# ============================== # RUNNING WebSocket Server # ==============================
async def run_server(host: str = "127.0.0.1", port: int = 8765):
    server = WebsocketServer(host, port)
    await server.start()
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await server.stop()