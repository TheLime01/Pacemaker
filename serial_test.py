
import serial
import serial.tools.list_ports
import time
import struct

print("\nports:")
for p in serial.tools.list_ports.comports():
    print(p.device, "-", p.description)


# Serial configuration
PORT = "COM10"
BAUD = 115200

# Packet constants
SYNC = 0x16
FN_CODE = 0x55  # 0x55 setting params, 0x22 echo
RED_ENABLE = 1
GREEN_ENABLE = 1
BLUE_ENABLE = 1
OFF_TIME = 0.5       # float32 (seconds)
SWITCH_TIME = 200    # uint16 (milliseconds)


# Build packet: < = little-endian, B=uint8, f=float32, H=uint16
packet = struct.pack("<BBBBBfH",
                     SYNC, FN_CODE,
                     RED_ENABLE, GREEN_ENABLE, BLUE_ENABLE,
                     OFF_TIME, SWITCH_TIME)

print(f"Packet ({len(packet)} bytes):", " ".join(f"{b:02X}" for b in packet))

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2) 

    ser.write(packet)
    ser.flush()
    print("Packet sent successfully.")

    # Optional: read response if device echoes back
    response = ser.read(11)  # Expect 11 bytes if echo
    if response:
        print("Response:", " ".join(f"{b:02X}" for b in response))
    else:
        print("No response received.")

    ser.close()
except serial.SerialException as e:
    print(f"Serial Port Error: {e}")
