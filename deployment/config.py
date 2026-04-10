"""
config.py
──────────
All tunable constants and the shared queues live here.
Every other module imports from this file — never from each other.
"""

import queue

# ── Camera ────────────────────────────────────────────────────
FRAME_W    = 640
FRAME_H    = 480
FRAMERATE  = 30

# ── Detection thresholds ──────────────────────────────────────
WARN_THRESHOLD  = 0.05   # confidence ≥ this  → Warning
TRACK_THRESHOLD = 0.02   # confidence ≥ this  → Tracking + servo

# ── Serial (Arduino) ──────────────────────────────────────────
SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD = 9600

# ── Tracking dead-zone (pixels around frame centre) ───────────
DEAD_ZONE_X = 20
DEAD_ZONE_Y = 20

# ── Shared queues ─────────────────────────────────────────────
warn_queue:  queue.Queue = queue.Queue(maxsize=10)   # DD → W
track_queue: queue.Queue = queue.Queue(maxsize=10)   # DD → T
