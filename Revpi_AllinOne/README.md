Websocket server + test client
Websocket server (server-only branch)
====================================

This branch is focused on the websocket server only. The server groups
connections by path (topic) and relays JSON messages between clients that
share the same path. The client code exists in the repo for reference but
this branch's CLI and documentation are server-centric.

Usage
-----

Start the server:

```pwsh
python .\main.py --log debug
```

The server will listen on the configured host/port (defaults: 127.0.0.1:8765)
and log handshake details, subscriptions, and relayed messages.

Postman / manual subscribe
--------------------------

If you connect a generic WebSocket client (e.g. Postman) to a path like
`ws://127.0.0.1:8765/sensor/temp` and it doesn't appear to receive messages,
send a subscribe control message after connecting:

```json
{"join": "/sensor/temp"}
```

```json
{"leave": "/sensor/temp"}
```

The server will respond with an ack: `{ "status": "joined", "path": "/sensor/temp" }` & `{ "status": "leave", "path": "/sensor/temp" }`.

Files of interest
-----------------

- `server.py` - the server implementation and connection handler
- `handlers/message.py` - message processing logic (control/data handling)
- `main.py` - CLI entrypoint (server-only in this branch)

