# RevPi WebSocket Controller

Modul ini adalah **runtime client controller RevPi** dalam arsitektur 2-RevPi
(Controller ↔ Gateway ↔ Dashboard). Controller ini yang terhubung langsung
ke hardware fisik (push button, LED, buzzer, relay, sensor), sedangkan
Gateway (project terpisah, lihat `revpi_gateway_fixed`) menjadi perantara
antara Controller dan dashboard web.

Controller terhubung ke gateway, mengirim telemetry berkala, menerima
command aktuator, membalas ACK, dan mencatat semua log ke SQLite + CSV.

---

## Update / Fix yang sudah diterapkan

Project ini pernah punya beberapa bug yang menyebabkan **input dari
dashboard berfungsi normal, tapi input fisik (tombol/hardware) tidak
responsif atau LED kedap-kedip**. Berikut fix yang sudah masuk:

1. **`revpi/rpi_core.py` (baru)** — sebelumnya `revpi/data_provider.py`
   dan `revpi/sensor.py` masing-masing membuat instance
   `revpimodio2.RevPiModIO(autorefresh=True)` sendiri-sendiri. Dua instance
   autorefresh berjalan bersamaan di proses yang sama saling rebutan akses
   ke process image, sehingga pembacaan input fisik jadi tidak konsisten.
   Sekarang **hanya ada satu instance `rpi` yang dipakai bersama**, semua
   modul lain wajib import dari `revpi/rpi_core.py`, jangan pernah membuat
   instance baru.

2. **`--id` sekarang benar-benar dipakai** — sebelumnya argumen `--id` di
   CLI dibaca tapi tidak pernah diteruskan ke `client_revpi.py`, yang
   hardcode `CONTROLLER_ID = "revpi01"`. Sekarang `main.py` memanggil
   `set_controller_id()` sehingga id yang didaftarkan ke gateway sesuai
   dengan yang kamu berikan lewat `--id`. **Default `--id` = `revpi01`**,
   disamakan dengan fallback target di gateway, supaya dashboard yang
   tidak mengirim `"target"` tetap otomatis nyambung ke controller ini.
   Kalau kamu jalankan lebih dari satu controller, wajib beri `--id`
   berbeda untuk tiap unit, dan pastikan dashboard mengirim `"target"`
   yang sesuai.

3. **`scenarios/io_test_case.py` — fix LED kedap-kedip** — sebelumnya
   loop scenario ini menulis ulang output setiap 100ms **tanpa peduli
   mode LOCAL/REMOTE**, sehingga bentrok dengan command LED yang dikirim
   langsung dari dashboard saat mode REMOTE (dua sumber saling menimpa
   → LED terlihat kedap-kedip). Sekarang scenario **hanya menulis ke
   hardware saat `MODE=LOCAL`**; saat `MODE=REMOTE`, penulisan output
   sepenuhnya diserahkan ke command dashboard (`apply_control_command`).

4. **`check_io.py` (baru)** — script diagnostik untuk memverifikasi
   wiring, terutama posisi selector `SW10` (LOCAL/REMOTE) dan status
   `EM9` (emergency stop), karena keduanya bisa membuat sistem *terlihat*
   seperti tidak merespon padahal itu memang logika yang disengaja.

5. **`revpi/data_provider.py` — fix logic NO/NC tombol** — hasil
   diagnostik lapangan menunjukkan **PB1-PB4 memakai tombol NO**
   (idle=0, ditekan=1) sedangkan **PB5-PB8 memakai tombol NC**
   (idle=1, ditekan=0). Sebelumnya semua PB dibaca mentah tanpa
   dibedakan, sehingga di `actuator.py`, LED2-LED5 (yang di-drive oleh
   PB5-PB8) justru **menyala saat idle dan mati saat ditekan** —
   terbalik dari yang diharapkan. Sekarang `read_all()` meng-invert
   PB5-PB8 di titik pembacaan, sehingga nilai yang diteruskan ke seluruh
   sistem (`actuator.py`, dashboard, scenario lain) selalu bermakna
   **`1 = ditekan`** untuk semua tombol, NO maupun NC.

---

## Instalasi

```bash
cd revpi_controller_fixed
pip install -r requirements.txt
```

## Menjalankan Controller

```bash
python3 main.py --host <IP_GATEWAY> --port 8765 --id revpi01 --mode io --log info
```

| Argumen   | Default        | Keterangan |
|-----------|----------------|------------|
| `--host`  | `192.168.1.106`| IP RevPi Gateway. **Wajib disesuaikan** dengan IP gateway aktual di jaringanmu (cek dengan `hostname -I` di RevPi gateway). |
| `--port`  | `8765`         | Port websocket gateway. |
| `--id`    | `revpi01`      | ID unik controller ini saat mendaftar ke gateway. Harus cocok dengan `"target"` yang dikirim dashboard. |
| `--mode`  | `io`           | Skenario yang dijalankan: `io`, `logic`, `traffic`, `process`, `conveyor` (lihat folder `scenarios/`). |
| `--log`   | `info`         | Level log: `info` atau `debug`. |

Urutan yang disarankan:
1. Jalankan **gateway** terlebih dahulu (`revpi_gateway_fixed`).
2. Jalankan **controller** ini.
3. Cek log di gateway — harus muncul `REGISTERED CONTROLLER` dengan id
   yang sesuai. Kalau tidak muncul, cek kembali `--host`/firewall/port.
4. Baru buka dashboard/web client, kirim handshake `{"role": "web"}`,
   lalu boleh mulai kirim command.

## Diagnostik I/O (sebelum curiga ada bug software)

Sebelum menyalahkan kode, cek dulu wiring fisik dengan:

```bash
python3 check_io.py
```

Script ini mencetak nilai mentah `PB1–PB8`, `EM9`, `SW10–SW14` tiap 0.5
detik. Yang perlu diperhatikan:

- **`SW10` = selector LOCAL/REMOTE.** `SW10=0` → tombol fisik langsung
  mengendalikan output (LOCAL). `SW10=1` → hanya dashboard yang bisa
  mengendalikan output (REMOTE), tombol fisik PB1-PB8 sengaja diabaikan.
- **`EM9` = emergency stop.** Kalau `EM9=0`, `io_test_case.py` akan
  memaksa **semua output mati** (kecuali LED6/indikator emergency yang
  menyala). Kalau `EM9` belum di-wire / floating di 0, semua LED akan
  terlihat "tidak merespon" walau tombol lain ditekan — ini sengaja untuk
  keperluan safety, bukan bug.

## Postman / command flow reference

Handshake otomatis saat controller connect ke gateway:
```json
{"role": "controller", "id": "revpi01"}
```

Command dari gateway ke controller ini (contoh mengubah LED1):
```json
{"type": "command", "target": "revpi01", "payload": {"LED1": true}}
```

Balasan ACK dari controller:
```json
{"type": "ack", "source": "revpi01", "command_id": "cmd_0001", "status": "ok"}
```

Telemetry (data sensor) dan indicator (status LED/output) dikirim otomatis
secara periodik/event-driven ke gateway, lalu diteruskan ke semua web
client yang terhubung.

## Files of interest

* `main.py` — entrypoint controller, parsing argumen CLI
* `revpi/rpi_core.py` — **instance `RevPiModIO` tunggal**, dipakai bersama semua modul
* `revpi/client_revpi.py` — worker komunikasi websocket & telemetry loop
* `revpi/data_provider.py` — akses I/O fisik (baca sensor/input, tulis output)
* `revpi/input_manager.py` — logic switching input hardware vs dashboard (berdasar `SW10`)
* `revpi/logging.py` — logging SQLite + CSV
* `scenarios/` — skenario kontrol (io test, logic gate, traffic light, mini process, conveyor counter)
* `check_io.py` — script diagnostik nilai mentah digital input
