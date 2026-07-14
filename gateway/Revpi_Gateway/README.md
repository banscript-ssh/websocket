# RevPi WebSocket Gateway

Modul ini adalah **server gateway WebSocket** dalam arsitektur 2-RevPi
(Controller ↔ Gateway ↔ Dashboard) untuk komunikasi IIoT real-time.
Gateway ini menangani registrasi controller, koneksi web client (dashboard),
routing command, forwarding telemetry, dan ACK — tapi **tidak menyentuh
hardware sama sekali**. Semua akses fisik (push button, LED, sensor, dll)
ada di project `revpi_controller_fixed` yang berjalan di RevPi terpisah.

---

## Cara kerja routing (penting untuk debugging)

Setiap client yang connect ke gateway wajib kirim handshake pertama:

- Controller: `{"role": "controller", "id": "revpi01"}`
- Web/dashboard: `{"role": "web"}`

Setelah itu:

- **Command dari web** → gateway bungkus jadi
  `{"type": "command", "target": ..., "payload": {...}}` lalu diteruskan
  ke controller dengan `id` yang cocok dengan `"target"`.
  **Kalau web client tidak mengirim `"target"` sama sekali, gateway akan
  memakai default `"revpi01"`.** Karena itu, di sisi controller kami set
  default `--id revpi01` juga (lihat README `revpi_controller_fixed`) —
  supaya setup 1 controller bisa langsung jalan tanpa perlu dashboard
  menyebutkan target secara eksplisit.
- **Telemetry (`type: data`) & indicator (`type: indicator`)** dari
  controller → langsung di-broadcast ke semua web client yang terhubung.
- **ACK (`type: ack`)** dari controller → diteruskan ke semua web client.

Kalau kamu menjalankan lebih dari satu controller, setiap controller wajib
punya `id` unik, dan dashboard wajib mengirim `"target"` yang sesuai saat
mengirim command — kalau tidak, semua command akan selalu diarahkan ke
`revpi01`.

---

## Instalasi

```bash
cd revpi_gateway_fixed
pip install -r requirements.txt
```

## Menjalankan Gateway

```bash
python3 main.py --host 0.0.0.0 --port 8765 --log info
```

| Argumen  | Default   | Keterangan |
|----------|-----------|------------|
| `--host` | `0.0.0.0` | Bind ke semua interface, supaya controller & dashboard dari IP mana pun di jaringan lokal bisa connect. |
| `--port` | `8765`    | Port websocket server. |
| `--log`  | `info`    | Level log: `info` atau `debug` (pakai `debug` saat troubleshooting routing command). |

Gateway juga otomatis menjalankan:
- **Heartbeat monitor** — log jumlah controller & web client aktif tiap 5 detik.
- **UDP beacon** (port `9999`, tiap 2 detik) — supaya controller bisa
  auto-discover IP gateway ini tanpa perlu di-hardcode, meskipun IP-nya
  berubah-ubah (DHCP).

## Urutan running yang disarankan

1. Jalankan **gateway** ini terlebih dahulu.
2. Jalankan **controller** (`revpi_controller_fixed`), pastikan `--host`
   di controller mengarah ke IP gateway ini.
3. Cek log gateway — harus muncul:
   ```
   ========== REGISTERED CONTROLLER ==========
   {'revpi01': <websocket>}
   ```
   Kalau tidak muncul dalam beberapa detik, cek IP `--host` di controller
   dan pastikan port `8765` tidak diblokir firewall.
4. Baru buka dashboard/web client, connect ke `ws://<IP_GATEWAY>:8765`,
   kirim handshake `{"role": "web"}`, baru boleh kirim command.

## Postman / manual command (testing tanpa dashboard asli)

Connect websocket client (misalnya Postman) ke:
```
ws://<IP_GATEWAY>:8765
```

Kirim handshake:
```json
{"role": "web"}
```

Kirim command (contoh menyalakan LED1 di controller `revpi01`):
```json
{"type": "command", "target": "revpi01", "LED1": true}
```

Gateway akan meneruskan ke controller yang sesuai dan merelay ACK +
telemetry balik ke semua web client yang terhubung.

## Files of interest

* `main.py` — entrypoint CLI gateway
* `app/server.py` — implementasi server & registry controller/web client
* `app/discovery.py` — UDP beacon untuk auto-discovery controller
* `app/handlers/messages.py` — logic routing command, telemetry, ACK
* `utils/csv_logger.py` — logging CSV sisi gateway