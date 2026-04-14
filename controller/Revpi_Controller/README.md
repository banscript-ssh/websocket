# RevPi WebSocket Controller

# RevPi edge client (controller branch)

This module is focused on the **RevPi controller runtime client**.
The controller connects to the gateway, sends periodic telemetry, receives actuator commands, returns ACK responses, and pushes reflected telemetry events.

## Usage

Start the controller:

```bash
python .\main.py --host 127.0.0.1 --port 8765 --id C1
```

The controller connects to the gateway server, sends telemetry every 1 second, executes actuator commands, and logs measurements using SQLite + CSV.

## Postman / command flow reference

The controller starts with an automatic handshake:

```json
{"role": "controller", "id": "C1"}
```

When receiving a command from the gateway:

```json
{"type": "command", "target": "C1", "LED1": true}
```

it responds with:

```json
{"type": "ack", "source": "C1", "command_id": "cmd-001", "status": "ok"}
```

Telemetry data is sent automatically in periodic and event-driven mode.

## Files of interest

* `main.py` - controller runtime entrypoint
* `client_revpi.py` - communication worker and telemetry loop
* `logging.py` - SQLite + CSV logging
* `test_cases/` - logic gate, traffic light, and mini process control
