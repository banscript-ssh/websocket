# ============================== # IMPORT LIBRARY # ============================== #
import asyncio
import json
import logging
import websockets

from typing import Optional
from app.handlers.messages import handle_message

logger = logging.getLogger("app/server")

# ============================== # WEBSOCKET GATEWAY SERVER # ============================== #
class WebSocketGatewayServer:

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8765
    ):

        self.host = host
        self.port = port

        self.controllers: dict[str, websockets.WebSocketServerProtocol] = {}
        self.web_clients: set[websockets.WebSocketServerProtocol] = set()
        self._clients: set[websockets.WebSocketServerProtocol] = set()

        self._server: Optional[
            websockets.server.Serve
        ] = None

        self.command_counter = 0

    # ============================== # GENERATE CORRELATION ID # ============================== #
    def generate_correlation_id(self) -> str:
        self.command_counter += 1
        return f"cmd_{self.command_counter:04d}"

    # ============================== # HANDLER CLIENT WEBSOCKET # ============================== #
    async def handler(
        self,
        websocket,
        path=None
    ):

        peer = websocket.remote_address

        print("\n========================================")
        print("[CONNECT] Client Connected")
        print(f"Address : {peer}")
        print("========================================")

        logger.info(
            "Client connected: %s",
            peer
        )

        self._clients.add(websocket)

        role = None
        client_id = None

        try:
            # ============================== # HANDSHAKE # ============================== #
            init_msg = await websocket.recv()

            try:
                data = json.loads(init_msg)

            except json.JSONDecodeError:
                logger.warning(
                    "[HANDSHAKE] Invalid JSON from %s",
                    peer
                )

                await websocket.close()\

            # ============================== # REGISTER CLIENT # ============================== #
            role = data.get("role")
            client_id = data.get("id")

            print("\n========== REGISTER ==========")
            print(f"Role : {role}")
            print(f"ID   : {client_id}")
            print("==============================")

            if role == "controller":
                self.controllers[client_id] = websocket

                print("\n========== REGISTERED CONTROLLER ==========")
                print(self.controllers)
                print("===========================================")

            elif role == "web":
                self.web_clients.add(websocket)

            else:
                logger.warning(
                    "[HANDSHAKE] Unknown role : %s",
                    role
                )

                await websocket.close()
                return

            print("\n========== ACTIVE CLIENT ==========")
            print(f"Controllers : {len(self.controllers)}")
            print(f"Web Clients : {len(self.web_clients)}")
            print(f"Total Client: {len(self._clients)}")
            print("===================================")

            # ============================== # RECEIVE MESSAGE # ============================== #
            async for message in websocket:
                try:
                    msg = json.loads(message)

                    print("\n========== RX ==========")
                    print(f"From : {client_id}")
                    print(f"Type : {msg.get('type')}")
                    print(msg)
                    print("========================")

                except json.JSONDecodeError:
                    logger.warning(
                        "[RX] Invalid JSON from %s",
                        client_id
                    )
                    continue

                try:
                    await handle_message(
                        websocket,
                        message,
                        self,
                        peer
                    )

                except Exception:
                    logger.exception(
                        "[MESSAGE] Error handling message"
                    )

        # ============================== # CLIENT DISCONNECT # ============================== #
        finally:

            print("\n========================================")
            print("[DISCONNECT]")
            print(f"Role : {role}")
            print(f"ID   : {client_id}")
            print("========================================")

            self._clients.discard(websocket)

            if role == "controller" and client_id:
                self.controllers.pop(
                    client_id,
                    None
                )

            elif role == "web":
                self.web_clients.discard(
                    websocket
                )

            print("\n========== ACTIVE CLIENT ==========")
            print(f"Controllers : {len(self.controllers)}")
            print(f"Web Clients : {len(self.web_clients)}")
            print(f"Total Client: {len(self._clients)}")
            print("===================================")

    # ============================== # SEND TO CONTROLLER # ============================== #
    async def send_to_controller(
        self,
        controller_id: str,
        payload: str
    ):

        ws = self.controllers.get(controller_id)
        if ws is None:

            logger.warning(
                "[TX] Controller %s not connected",
                controller_id
            )

            return False

        try:
            await ws.send(payload)

            logger.info(
                "[TX] Command sent -> %s",
                controller_id
            )

            return True
        except Exception:

            logger.exception(
                "[TX] Failed sending command to %s",
                controller_id
            )

            self.controllers.pop(
                controller_id,
                None
            )

            return False

    # ============================== # BROADCAST TO WEB # ============================== #
    async def broadcast_to_web(
        self,
        payload: str
    ):

        dead = set()

        for ws in self.web_clients:

            try:
                await ws.send(payload)

            except Exception:
                logger.exception(
                    "[TX] Web Client Disconnected"
                )
                dead.add(ws)

        self.web_clients -= dead

    # ============================== # FORWARD ACK TO WEB # ============================== #
    async def forward_ack_to_web(
        self,
        payload: str
    ):

        await self.broadcast_to_web(payload)

    # ============================== # MONITOR ACTIVE CLIENTS # ============================== #
    async def monitor_clients(self):

        while True:
            logger.info(
                "[MONITOR] controllers=%d web=%d total=%d",
                len(self.controllers),
                len(self.web_clients),
                len(self._clients)
            )

            await asyncio.sleep(5)

    # ============================== # START SERVER # ============================== #
    async def start(self):

        self._server = await websockets.serve(
            self.handler,
            self.host,
            self.port
        )

    # ============================== # STOP SERVER # ============================== #
    async def stop(self):

        if self._server:
            self._server.close()
            await self._server.wait_closed()