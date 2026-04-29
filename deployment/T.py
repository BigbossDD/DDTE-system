import time
import queue
import serial

from config import FRAME_W, FRAME_H, SERIAL_PORT, SERIAL_BAUD, track_queue

# ── PARAMETERS ───────────────────────────────────────────────
CONF_THRESHOLD = 0.30          # minimum confidence to start tracking
SEND_INTERVAL  = 0.05          # limit serial updates (20 Hz max)

# servo physical limits (protect hardware)
PAN_MIN, PAN_MAX   = 10, 170
TILT_MIN, TILT_MAX = 10, 160

# control tuning (PD controller)
KP = 0.0020                    # proportional gain → reacts to position error
KD = 0.0015                    # derivative gain → dampens overshoot (anti-jiggle)

MAX_STEP = 2.5                 # max movement per update (limits speed)

# input smoothing (low-pass filter)
ALPHA = 0.25                   # higher = faster response, lower = smoother

# ignore small errors near center (prevents jitter)
DEAD_ZONE = 15                 # pixels

# reject sudden detection jumps (YOLO instability)
MAX_JUMP = 120                 # pixels

# smooth servo velocity (inertia effect)
VEL_SMOOTH = 0.7               # higher = smoother but slower response

# ── STATE ────────────────────────────────────────────────────
pan  = 70.0                    # initial servo position (horizontal)
tilt = 40.0                    # initial servo position (vertical)

# velocity state (used for smoothing movement)
vel_pan  = 0.0
vel_tilt = 0.0

# previous error (for derivative term)
last_err_x = 0
last_err_y = 0

# last raw detection (for jump filtering)
last_cx = None
last_cy = None

# smoothed detection (low-pass filtered)
smooth_cx = None
smooth_cy = None

# last time we sent a command to Arduino
last_send = 0

# frame center (target point)
cx0 = FRAME_W / 2
cy0 = FRAME_H / 2

# ── LASER CONTROL ───────────────────────────────
LASER_THRESHOLD = 0.50         # confidence needed to activate laser
LASER_DURATION  = 5.0          # how long laser stays ON (seconds)

laser_active = False           # current laser state
laser_end_time = 0             # when to turn laser OFF


# ── SERIAL CONNECTION ───────────────────────────
def open_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD)
        time.sleep(2)          # allow Arduino to reset
        print("[T] Serial connected")
        return ser
    except:
        print("[T] Serial FAILED")
        return None


# ── MAIN TRACKING LOOP ──────────────────────────
def run_T():
    global pan, tilt, vel_pan, vel_tilt
    global last_err_x, last_err_y
    global last_send, last_cx, last_cy, smooth_cx, smooth_cy

    ser = open_serial()
    print("[T] Tracking started")

    while True:
        try:
            data = track_queue.get(timeout=1)
        except queue.Empty:
            continue

        cx   = data["cx"]           # detected object center X
        cy   = data["cy"]           # detected object center Y
        conf = data["confidence"]   # detection confidence

        # ignore weak detections
        if conf < CONF_THRESHOLD:
            continue

        now = time.time()

        # ── LASER CONTROL (STATE-BASED) ─────────────────────
        global laser_active, laser_end_time

        # trigger laser once when threshold is crossed
        if conf >= LASER_THRESHOLD and not laser_active:
            if ser and ser.is_open:
                ser.write(b"LON\n")
                print("[T] LASER ON")
                laser_active = True
                laser_end_time = now + LASER_DURATION

        # turn laser OFF after timer expires
        if laser_active and now >= laser_end_time:
            if ser and ser.is_open:
                ser.write(b"LOFF\n")
                print("[T] LASER OFF")
            laser_active = False

        # ── FILTER BAD DETECTIONS ───────────────────────────
        # ignore sudden jumps (usually YOLO glitch)
        if last_cx is not None:
            if abs(cx - last_cx) > MAX_JUMP or abs(cy - last_cy) > MAX_JUMP:
                continue

        last_cx, last_cy = cx, cy

        # ── SMOOTH DETECTION (LOW-PASS FILTER) ──────────────
        if smooth_cx is None:
            smooth_cx, smooth_cy = cx, cy
        else:
            smooth_cx = (1 - ALPHA) * smooth_cx + ALPHA * cx
            smooth_cy = (1 - ALPHA) * smooth_cy + ALPHA * cy

        # ── COMPUTE ERROR (TARGET - CENTER) ─────────────────
        err_x = smooth_cx - cx0
        err_y = smooth_cy - cy0

        # dead zone: ignore tiny movements near center
        if abs(err_x) < DEAD_ZONE:
            err_x = 0
        if abs(err_y) < DEAD_ZONE:
            err_y = 0

        # ── PD CONTROL (CORE OF SMOOTH TRACKING) ────────────
        # derivative term reduces overshoot (predicts movement)
        d_err_x = err_x - last_err_x
        d_err_y = err_y - last_err_y

        last_err_x = err_x
        last_err_y = err_y

        # adaptive gain: stronger correction when far from center
        gain_scale = min(1.5, abs(err_x) / 200 + 0.5)

        # compute movement step
        step_pan  = -(KP * gain_scale * err_x + KD * d_err_x)
        step_tilt = -(KP * gain_scale * err_y + KD * d_err_y)

        # limit speed (prevents sudden jumps)
        step_pan  = max(-MAX_STEP, min(MAX_STEP, step_pan))
        step_tilt = max(-MAX_STEP, min(MAX_STEP, step_tilt))

        # ── VELOCITY SMOOTHING ──────────────────────────────
        # acts like inertia → smoother, more natural movement
        vel_pan  = VEL_SMOOTH * vel_pan  + (1 - VEL_SMOOTH) * step_pan
        vel_tilt = VEL_SMOOTH * vel_tilt + (1 - VEL_SMOOTH) * step_tilt

        # update servo positions
        pan  += vel_pan
        tilt += vel_tilt

        # enforce physical limits
        pan  = max(PAN_MIN,  min(PAN_MAX,  pan))
        tilt = max(TILT_MIN, min(TILT_MAX, tilt))

        # ── SEND TO ARDUINO ─────────────────────────────────
        now = time.time()
        if ser and ser.is_open and now - last_send > SEND_INTERVAL:
            msg = f"{int(pan)},{int(tilt)}\n"
            ser.write(msg.encode())
            last_send = now

            # debug output (helps tuning)
            print(f"[T] pan={int(pan)} tilt={int(tilt)} "
                  f"err=({err_x:.0f},{err_y:.0f}) "
                  f"vel=({vel_pan:.2f},{vel_tilt:.2f}) "
                  f"conf={conf:.2f}")