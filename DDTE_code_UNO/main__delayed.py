"""
main.py
────────
Entry point. Starts W and T as background threads, then
runs DD on the main thread.
"""

import sys
import threading

from config import SERIAL_PORT, SERIAL_BAUD, WARN_THRESHOLD, TRACK_THRESHOLD
from DD import run_DD
from W  import run_W
from T  import run_T


if __name__ == "__main__":

    # Optional weights (only needed for YOLO mode)
    weights = sys.argv[1] if len(sys.argv) >= 2 else None

    print(f"[main] Warn threshold  : {WARN_THRESHOLD:.0%}")
    print(f"[main] Track threshold : {TRACK_THRESHOLD:.0%}")
    print(f"[main] Serial port     : {SERIAL_PORT} @ {SERIAL_BAUD}")

    if weights:
        print(f"[main] Using YOLO weights: {weights}")
    else:
        print("[main] Using FACE detection mode (no weights)")

    t_warn  = threading.Thread(target=run_W, daemon=True, name="Warning")
    t_track = threading.Thread(target=run_T, daemon=True, name="Tracking")

    t_warn.start()
    t_track.start()

    run_DD(weights)   # works for both modes