import time
import queue
import serial

from config import (
    FRAME_W, FRAME_H,
    SERIAL_PORT, SERIAL_BAUD,
    track_queue,
)

# ── control ─────────────────────────
CONF_THRESHOLD = 0.30
SEND_INTERVAL = 0.05

last_send = 0

# frame center
cx0 = FRAME_W // 2
cy0 = FRAME_H // 2

# open serial
def open_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD)
        time.sleep(2)
        print("[T] Serial connected")
        return ser
    except:
        print("[T] Serial FAILED (check /dev/ttyACM0)")
        return None


def run_T():
    global last_send

    ser = open_serial()
    print("[T] Tracking started")

    while True:
        try:
            data = track_queue.get(timeout=1)
        except queue.Empty:
            continue

        cx = data["cx"]
        cy = data["cy"]
        conf = data["confidence"]

        if conf < CONF_THRESHOLD:
            continue

        # error (pixel space)
        err_x = cx - cx0
        err_y = cy - cy0

        # convert to servo targets (VERY SIMPLE)
        pan = 90 + (err_x * 0.05)
        tilt = 90 + (err_y * 0.05)

        # clamp safe range
        pan = max(10, min(170, int(pan)))
        tilt = max(10, min(160, int(tilt)))

        now = time.time()
        if ser and ser.is_open and now - last_send > SEND_INTERVAL:
            msg = f"{pan},{tilt}\n"
            ser.write(msg.encode())
            last_send = now

            print(f"[T] send -> {msg.strip()}  conf={conf:.2f}")