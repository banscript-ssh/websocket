# ============================== # IMPORT LIBRARY # ==============================
import time
import math
import serial
import revpimodio2

# ============================== # INIT REVPI # ==============================
rpi = revpimodio2.RevPiModIO(autorefresh=True)
io = rpi.io

# ============================== # CHANNEL KONSTANTA # ==============================
SIGNAL_GEN_CHANNEL = "InputValue_1"   # µA
RTD_CHANNEL        = "RTDValue_1"     # PT1000

def truncate_float(val, n=2):
    return math.trunc(val * (10 ** n)) / (10 ** n)

# ============================== # ANALOG READ # ==============================
def read_signal_generator():
    try:
        raw_uA = io[SIGNAL_GEN_CHANNEL].value
        return raw_uA, raw_uA / 1000.0
    except:
        return None, None

def read_rtd_pt1000():
    try:
        raw = io[RTD_CHANNEL].value
        return raw, raw / 10.0   # 0.1 °C resolution
    except:
        return None, None

# # ==============================
# # MODBUS MD02 (CRC SUDAH FIX)
# # ==============================
# CMD_TEMP = bytes.fromhex("01 04 00 01 00 01 60 0A")
# CMD_HUM  = bytes.fromhex("01 04 00 02 00 01 90 0A")

# def read_md02(cmd):
#     try:
#         with serial.Serial(
#             port="/dev/ttyRS485",
#             baudrate=9600,
#             parity=serial.PARITY_NONE,
#             stopbits=serial.STOPBITS_ONE,
#             bytesize=serial.EIGHTBITS,
#             timeout=1
#         ) as ser:
#             ser.write(cmd)
#             time.sleep(0.4)            # WAJIB untuk MD02
#             resp = ser.read(16)

#         if len(resp) >= 7 and resp[1] == 0x04:
#             raw = int.from_bytes(resp[3:5], byteorder="big", signed=True)
#             return raw / 10.0
#         return None
#     except Exception as e:
#         print("MD02 Error:", e)
#         return None

# ==============================
# MAIN LOOP
# ==============================
# def main():
#     print("\n===== MONITORING SENSOR REVPI =====\n")

#     while True:
#         print("=== DATA SENSOR ===")

#         # --- 4–20 mA ---
#         raw_uA, mA = read_signal_generator()
#         if raw_uA is not None:
#             print(f"Signal Generator : {raw_uA} µA -> {mA:.3f} mA")
#         else:
#             print("Signal Generator : ERROR")

#         # --- RTD PT1000 ---
#         raw_rtd, rtd_temp = read_rtd_pt1000()
#         if raw_rtd is not None:
#             print(f"RTD PT1000       : RAW={raw_rtd} -> {truncate_float(rtd_temp,1)} °C")
#         else:
#             print("RTD PT1000       : ERROR")

#         # # --- MD02 ---
#         # temp = read_md02(CMD_TEMP)
#         # hum  = read_md02(CMD_HUM)

#         # if temp is not None:
#         #     print(f"MD02 Temperature : {temp:.1f} °C")
#         # else:
#         #     print("MD02 Temperature : ERROR")

#         # if hum is not None:
#         #     print(f"MD02 Humidity    : {hum:.1f} %RH")
#         # else:
#         #     print("MD02 Humidity    : ERROR")

#         print("-" * 35)
#         time.sleep(2)

# # ==============================
# if __name__ == "__main__":
#     main()
