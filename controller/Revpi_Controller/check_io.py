# ============================================================== #
# DIAGNOSTIC: cek nilai mentah semua digital input tiap 0.5 detik
# ============================================================== #
#
# Jalankan langsung di RevPi controller (bukan lewat websocket):
#   python3 check_io.py
#
# Tekan CTRL+C untuk berhenti.
#
# Gunanya:
# 1. Pastikan PB1-PB8 berubah 0 -> 1 saat tombol fisik ditekan.
# 2. Cek nilai SW10 (selector LOCAL/REMOTE).
#      SW10 = 0 -> get_input() akan mengembalikan HARDWARE langsung
#                  (tombol fisik HARUS langsung mempengaruhi output).
#      SW10 = 1 -> get_input() mengembalikan nilai DASHBOARD
#                  (tombol fisik-PB akan DIABAIKAN, ini disengaja/by design).
#    Kalau SW10 tidak pernah 0 walau selector fisik sudah diarahkan ke
#    LOCAL, berarti ada masalah wiring/polaritas pada switch tsb.
# 3. Cek nilai EM9 (emergency stop).
#      io_test_case.py akan MEMATIKAN SEMUA output kalau EM9 == 0.
#    Kalau EM9 tidak wired / selalu default 0, semua LED/BUZZ akan
#    selalu terlihat "tidak merespon" walau PB ditekan, padahal ini
#    memang logika safety yang disengaja.
#
# ============================================================== #

import time
from revpi.data_provider import read_all, get_control_mode

print("=" * 60)
print("RAW DIGITAL INPUT MONITOR (CTRL+C untuk stop)")
print("=" * 60)

try:
    while True:
        data = read_all()

        print(
            f"MODE={get_control_mode():7s} | "
            f"PB1={data['PB1']} PB2={data['PB2']} PB3={data['PB3']} "
            f"PB4={data['PB4']} PB5={data['PB5']} PB6={data['PB6']} "
            f"PB7={data['PB7']} PB8={data['PB8']} | "
            f"EM9={data['EM9']} | "
            f"SW10={data['SW10']} SW11={data['SW11']} "
            f"SW12={data['SW12']} SW13={data['SW13']} SW14={data['SW14']}"
        )

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopped.")
