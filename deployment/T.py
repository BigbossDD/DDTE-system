import time
import queue
import serial

from config import FRAME_W, FRAME_H, SERIAL_PORT, SERIAL_BAUD, track_queue

# ── PARAMETERS ───────────────────────────────────────────────
CONF_THRESHOLD = 0.30
SEND_INTERVAL  = 0.05

# servo limits
PAN_MIN, PAN_MAX   = 10, 170
TILT_MIN, TILT_MAX = 10, 160

# control tuning
KP = 0.0022          # slightly lower = less aggressive
MAX_STEP = 2.5       # slower max speed = smoother

# smoothing
ALPHA = 0.25         # (0.1 = very smooth, 0.5 = fast response)

# dead zone (pixels)
DEAD_ZONE = 15

# jump rejection
MAX_JUMP = 120

# state
pan  = 70.0
tilt = 40.0

last_cx = None
last_cy = None

smooth_cx = None
smooth_cy = None

last_send = 0

cx0 = FRAME_W / 2
cy0 = FRAME_H / 2


# ── SERIAL ───────────────────────────────────────────────────
def open_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD)
        time.sleep(2)
        print("[T] Serial connected")
        return ser
    except:
        print("[T] Serial FAILED")
        return None


# ── MAIN LOOP ────────────────────────────────────────────────
def run_T():
    global pan, tilt, last_send
    global last_cx, last_cy, smooth_cx, smooth_cy

    ser = open_serial()
    print("[T] Tracking started")

    while True:
        try:
            data = track_queue.get(timeout=1)
        except queue.Empty:
            continue

        cx   = data["cx"]
        cy   = data["cy"]
        conf = data["confidence"]

        if conf < CONF_THRESHOLD:
            continue

        # ── Reject sudden jumps ──────────────────────────────
        if last_cx is not None:
            if abs(cx - last_cx) > MAX_JUMP or abs(cy - last_cy) > MAX_JUMP:
                continue

        last_cx, last_cy = cx, cy

        # ── Smooth the detection (LOW PASS FILTER) ───────────
        if smooth_cx is None:
            smooth_cx, smooth_cy = cx, cy
        else:
            smooth_cx = (1 - ALPHA) * smooth_cx + ALPHA * cx
            smooth_cy = (1 - ALPHA) * smooth_cy + ALPHA * cy

        # ── Compute error ────────────────────────────────────
        err_x = smooth_cx - cx0
        err_y = smooth_cy - cy0

        # ── Dead zone (prevents jitter near center) ─────────
        if abs(err_x) < DEAD_ZONE:
            err_x = 0
        if abs(err_y) < DEAD_ZONE:
            err_y = 0

        # ── Proportional control ────────────────────────────
        step_pan  = -KP * err_x
        step_tilt = -KP * err_y

        # ── Damping (VERY IMPORTANT) ────────────────────────
        step_pan  *= 0.85
        step_tilt *= 0.85

        # limit speed
        step_pan  = max(-MAX_STEP, min(MAX_STEP, step_pan))
        step_tilt = max(-MAX_STEP, min(MAX_STEP, step_tilt))

        # update position
        pan  += step_pan
        tilt += step_tilt

        # clamp
        pan  = max(PAN_MIN,  min(PAN_MAX,  pan))
        tilt = max(TILT_MIN, min(TILT_MAX, tilt))

        # ── send ────────────────────────────────────────────
        now = time.time()
        if ser and ser.is_open and now - last_send > SEND_INTERVAL:
            msg = f"{int(pan)},{int(tilt)}\n"
            ser.write(msg.encode())
            last_send = now

            print(f"[T] pan={int(pan)} tilt={int(tilt)} "
                  f"err=({err_x:.0f},{err_y:.0f}) "
                  f"step=({step_pan:.2f},{step_tilt:.2f}) "
                  f"conf={conf:.2f}")