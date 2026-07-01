# ============================== # IMPORT LIBRARY # ==============================
import asyncio
import logging
import json
from typing import Optional
import websockets
from app.handlers.messages import handle_message

logger = logging.getLogger("app/server")

# ============================== # PARSING CLASS WEBSOCKET GATEWAY SERVER # ==============================
class WebSocketGatewayServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.controllers: dict[str, websockets.WebSocketServerProtocol] = {}
        self.web_clients: set[websockets.WebSocketServerProtocol] = set()
        self.host = host
        self.port = port
        self._server: Optional[websockets.server.Serve] = None
        self._clients: set[websockets.WebSocketServerProtocol] = set()
        self.command_counter = 0

    # ============================== # GENERATE CORRELATION ID # ==============================
    def generate_correlation_id(self) -> str:
        self.command_counter += 1
        return f"cmd_{self.command_counter:04d}"

    # ============================== # HANDLER CLIENT WEBSOCKET # ==============================
    async def handler(self, websocket, path=None):

        peer = websocket.remote_address

        print("\n========================================")
        print("[CONNECT] Client Connected")
        print(f"Address : {peer}")
        print("========================================")

        logger.info("Client connected: %s", peer)

        self._clients.add(websocket)

        role = None
        client_id = None

        try:
            init_msg = await websocket.recv()
            data = json.loads(init_msg)

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
                return
            print("\n========== ACTIVE CLIENT ==========")
            print(f"Controllers : {len(self.controllers)}")
            print(f"Web Clients : {len(self.web_clients)}")
            print(f"Total Client: {len(self._clients)}")
            print("===================================")    
            async for message in websocket:
                print("\n========== RX ==========")
                print(f"From : {client_id}")
                print(message)
                print("========================")
                await handle_message(websocket, message, self, peer)

        finally:
            print("\n========================================")
            print("[DISCONNECT]")
            print(f"Role : {role}")
            print(f"ID   : {client_id}")
            print("========================================")


            self._clients.discard(websocket)
            if role == "controller" and client_id:
                self.controllers.pop(client_id, None)
            elif role == "web":
                self.web_clients.discard(websocket)
            print("\n========== ACTIVE CLIENT ==========")
            print(f"Controllers : {len(self.controllers)}")
            print(f"Web Clients : {len(self.web_clients)}")
            print(f"Total Client: {len(self._clients)}")
            print("===================================")
                
    # ============================== # SEND TO SPECIFIC CONTROLLER # ==============================
    async def send_to_controller(self, controller_id: str, payload: str):
        ws = self.controllers.get(controller_id)
        if ws:
            await ws.send(payload)

    # ============================== # BROADCAST TO WEB CLIENT # ==============================
    async def broadcast_to_web(self, payload: str):
        dead = set()
        for ws in self.web_clients:
            try:
                await ws.send(payload)
            except Exception:
                dead.add(ws)
        self.web_clients -= dead

    # ============================== # FORWARD ACK TO WEB # ==============================
    async def forward_ack_to_web(self, payload: str):
        await self.broadcast_to_web(payload)

    # ============================== # MONITOR ACTIVE CLIENTS # ==============================
    async def monitor_clients(self):
        while True:
            logger.info(
                "[MONITOR] controllers=%d web=%d total=%d",
                len(self.controllers),
                len(self.web_clients),
                len(self._clients)
            )
            await asyncio.sleep(5)

    async def start(self):
        self._server = await websockets.serve(self.handler, self.host, self.port)

    async def stop(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()