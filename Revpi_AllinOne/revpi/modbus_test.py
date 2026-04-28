import serial
import time

CMD_TEMP = bytes.fromhex("01 04 00 01 00 01 60 0A")
CMD_HUM  = bytes.fromhex("01 04 00 02 00 01 90 0A")

def parse(resp):
    if len(resp) >= 7 and resp[1] == 0x04:
        return int.from_bytes(resp[3:5], "big") / 10.0
    return None

with serial.Serial("/dev/ttyUSB0", 9600, timeout=1) as ser:
    while True:
        ser.write(CMD_TEMP)
        time.sleep(0.4)
        t = parse(ser.read(16))

        ser.write(CMD_HUM)
        time.sleep(0.4)
        h = parse(ser.read(16))

        print(f"TEMP: {t} °C | HUM: {h} %RH")
        time.sleep(2)
