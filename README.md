# RevPi WebSocket IIoT

# Gateway + controller repository (main branch)

This repository is focused on **real-time IIoT communication using Revolution Pi and WebSocket**.
The project is divided into two main modules:

* **Gateway** → WebSocket relay server for controller registration, command routing, telemetry forwarding, and ACK responses
* **Controller** → RevPi edge runtime client for sensor acquisition, actuator execution, periodic telemetry, and reflected telemetry

The repository also includes **documentation and study-case scenarios** for logic gate, traffic light, and mini process control.

## Usage

Start the gateway server:

```bash
cd gateway/Revpi_Gateway
python .\main.py --host 0.0.0.0 --port 8765 --log debug
```

Start the controller:

```bash
cd controller/Revpi_Controller
python .\main.py --host 127.0.0.1 --port 8765 --id C1
```

Default WebSocket server:

```text
ws://127.0.0.1:8765
```

## Postman / manual command

Connect Postman or a generic WebSocket client to:

```text
ws://127.0.0.1:8765
```

Send web handshake:

```json
{"role": "web"}
```

Send control command:

```json
{"type": "command", "target": "C1", "LED1": true}
```

Expected ACK response:

```json
{"type": "ack", "source": "C1", "command_id": "cmd-001", "status": "ok"}
```

## Files of interest

* `gateway/Revpi_Gateway/` - WebSocket gateway server module
* `controller/Revpi_Controller/` - RevPi controller runtime module
* `docs/` - architecture, testing, and study-case documentation
* `.gitignore` - ignored runtime and logging artifacts
