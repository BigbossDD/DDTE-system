"""
W.py  –  Warning
──────────────────
Consumes detection events from warn_queue and issues alerts.
Add buzzer / LED / network / sound logic in the marked section.
"""

import queue

from config import TRACK_THRESHOLD, warn_queue


def run_W():
    print("[W]  Warning section running.")

    while True:
        try:
            event = warn_queue.get(timeout=1)
        except queue.Empty:
            continue

        conf        = event["confidence"]
        x1, y1, x2, y2 = event["box"]
        level       = "TRACK" if conf >= TRACK_THRESHOLD else "WARN"

        print(f"[W]  [{level}]  confidence={conf:.2%}  "
              f"box=({x1:.0f},{y1:.0f})→({x2:.0f},{y2:.0f})")

        # ── TODO: add your alert logic below ─────────────────
        # Examples:
        #   GPIO.output(LED_PIN, GPIO.HIGH)
        #   buzzer.beep()
        #   requests.post(WEBHOOK_URL, json=event)
        # ─────────────────────────────────────────────────────
