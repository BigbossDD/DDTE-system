"""
T.py  –  Tracking
───────────────────
Consumes drone centre-points from track_queue, computes the
pan/tilt error from the frame centre, and sends direction
commands to the Arduino UNO over serial.

Command protocol (single ASCII byte per command):
    b'L'  →  pan  left
    b'R'  →  pan  right
    b'U'  →  tilt up
    b'D'  →  tilt down
    b'S'  →  centred — stop / hold position

Multiple commands can be sent per frame (e.g. b'R' then b'U').
The Arduino handles each byte independently.
----------------------------
a diffrent method of movement we ended picking

"""

import time
import queue

import serial

from config import (
    FRAME_W, FRAME_H,
    SERIAL_PORT, SERIAL_BAUD,
    DEAD_ZONE_X, DEAD_ZONE_Y,
    track_queue,
)
# ── Control parameters ───────────────────────────

PAN_MIN, PAN_MAX = 20, 160
TILT_MIN, TILT_MAX = 20, 140

Kp = 0.04   # tuning parameter (start small)

# current servo angles (state)
pan_angle = 90
tilt_angle = 90

last_send_time = 0
SEND_INTERVAL = 0.05   # 20 Hz 

alpha = 0.2
smooth_cx = None
smooth_cy = None
# ── Serial helpers ────────────────────────────────────────────

def _open_serial(port: str, baud: int):
    """Try to open serial port; return None on failure so T keeps running."""
    try:
        ser = serial.Serial(port, baud)
        time.sleep(2)           # wait for Arduino reset
        print(f"[T]  Serial open on {port} @ {baud}")
        return ser
    except serial.SerialException as e:
        print(f"[T]  WARNING: could not open serial port: {e}")
        print("[T]  Tracking will run but commands won't be sent.")
        return None


# ── Direction logic ───────────────────────────────────────────

# def _compute_commands(err_x: int, err_y: int) -> list:
#     """
#     Convert pixel error (drone centre vs frame centre) into
#     a list of single-byte direction commands.

#     Dead-zone filtering prevents jitter when the drone is
#     already close to the frame centre.
#     """
#     cmds = []

#     # pan (horizontal)
#     if err_x > DEAD_ZONE_X:
#         cmds.append(b'R')       # drone is right of centre → pan right
#     elif err_x < -DEAD_ZONE_X:
#         cmds.append(b'L')       # drone is left  of centre → pan left

#     # tilt (vertical)
#     if err_y > DEAD_ZONE_Y:
#         cmds.append(b'D')       # drone is below centre    → tilt down
#     elif err_y < -DEAD_ZONE_Y:
#         cmds.append(b'U')       # drone is above centre    → tilt up

#     # within dead-zone on both axes → hold position
#     if not cmds:
#         cmds.append(b'S')

#     return cmds
##########################################

#new method of movement : 
def _compute_angles(err_x: int, err_y: int):
    global pan_angle, tilt_angle

    # proportional movement
    MAX_STEP = 5  # max degrees per frame

    delta_pan  = max(-MAX_STEP, min(MAX_STEP, Kp * err_x))
    delta_tilt = max(-MAX_STEP, min(MAX_STEP, Kp * err_y))
    # update angles
    pan_angle  += delta_pan
    tilt_angle += delta_tilt

    # clamp to servo limits
    pan_angle  = max(PAN_MIN, min(PAN_MAX, pan_angle))
    tilt_angle = max(TILT_MIN, min(TILT_MAX, tilt_angle))

    return int(pan_angle), int(tilt_angle)

# ── Main loop ─────────────────────────────────────────────────

def run_T():
    print("[T]  Tracking section starting …")

    ser  = _open_serial(SERIAL_PORT, SERIAL_BAUD)
    fc_x = FRAME_W // 2        # frame centre X
    fc_y = FRAME_H // 2        # frame centre Y

    print("[T]  Tracking section running.")

    while True:
        try:
            data = track_queue.get(timeout=1)
        except queue.Empty:
            continue

        drone_cx: int   = data["cx"]
        drone_cy: int   = data["cy"]
        conf:     float = data["confidence"]
        if conf < 0.25:
            continue
                
        if smooth_cx is None:
            smooth_cx = drone_cx
            smooth_cy = drone_cy
        else:
            smooth_cx = alpha * drone_cx + (1 - alpha) * smooth_cx
            smooth_cy = alpha * drone_cy + (1 - alpha) * smooth_cy

        err_x = int(smooth_cx - fc_x)
        err_y = int(smooth_cy - fc_y)
        #err_x = drone_cx - fc_x    # + → drone is right of centre
        #err_y = drone_cy - fc_y    # + → drone is below  centre

        if abs(err_x) < DEAD_ZONE_X:
            err_x = 0
        if abs(err_y) < DEAD_ZONE_Y:
            err_y = 0
        
        pan, tilt = _compute_angles(err_x, err_y)
        
        now = time.time()
        if now - last_send_time < SEND_INTERVAL:
            continue
        last_send_time = now
        
        # send to Arduino
        if ser and ser.is_open:
            msg = f"{pan},{tilt}\n"
            ser.write(msg.encode())
            print(f"[T] Sent: {msg.strip()}")

        print(f"[T]  conf={conf:.2%}  "
            f"err=({err_x:+d},{err_y:+d})  "
            f"angles=({pan},{tilt})")
