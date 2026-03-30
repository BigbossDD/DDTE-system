"""
main.py
────────
Entry point. Starts W and T as background threads, then
runs DD on the main thread (cv2.imshow needs the main thread).

Usage:
    python main.py <path_to_yolo_weights.pt>
"""

import sys
import threading

from config import SERIAL_PORT, SERIAL_BAUD, WARN_THRESHOLD, TRACK_THRESHOLD
from DD import run_DD
from W  import run_W
from T  import run_T


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_yolo_weights.pt>")
        sys.exit(1)

    weights = sys.argv[1]

    print(f"[main] Warn threshold  : {WARN_THRESHOLD:.0%}")
    print(f"[main] Track threshold : {TRACK_THRESHOLD:.0%}")
    print(f"[main] Serial port     : {SERIAL_PORT} @ {SERIAL_BAUD}")

    t_warn  = threading.Thread(target=run_W,  daemon=True, name="Warning")
    t_track = threading.Thread(target=run_T,  daemon=True, name="Tracking")

    t_warn.start()
    t_track.start()

    run_DD(weights)   # blocks until 'q' is pressed or stream ends
