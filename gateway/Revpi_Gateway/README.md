# RevPi WebSocket Gateway

# WebSocket server (gateway branch)

This module is focused on the **WebSocket gateway server** for real-time IIoT communication.
The gateway handles controller registration, web client connections, command routing, telemetry forwarding, and ACK responses.

## Usage

Start the gateway server:

```bash
python .\main.py --host 0.0.0.0 --port 8765 --log debug
```

The server listens on the configured host/port (default: `127.0.0.1:8765`) and logs handshake details, controller registration, command routing, telemetry, and ACK messages.

## Postman / manual command

If you connect a generic WebSocket client (e.g. Postman) to:

```text
ws://127.0.0.1:8765
```

send a web handshake message after connecting:

```json
{"role": "web"}
```

To send a manual control command:

```json
{"type": "command", "target": "C1", "LED1": true}
```

The gateway will forward the command to the target controller and relay ACK + telemetry responses back to connected web clients.

## Files of interest

* `main.py` - CLI entrypoint for the WebSocket gateway server
* `app/server.py` - server implementation and client registry
* `app/handlers/messages.py` - command, telemetry, and ACK routing logic
* `utils/csv_logger.py` - gateway-side CSV logging
