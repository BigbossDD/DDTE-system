# DD(drone detection) is the detection section 
#this will use weights from a yolo model 
# and this goes on the Pi 5  , and it will recive video
# feed from a cam and it will detect the drone and give a 
# a prob of how likely it is a drone and then it will send that
# and if it crosses a threshold it will sent to the W(warning) section of the code 
# now also if it crosses a diffrent threshold it will send to the 
# the T(tracking) section it will send to it whats it need of mathmatics 
#points and stuff  and when the T recives the math data , it will talk to a arduino UNO and 
# it will move a servo to point/center the cam at the drone 
"""
DD.py  –  Drone Detection
──────────────────────────
Reads YUV420 frames from rpicam-vid, runs YOLO inference,
annotates the frame, and pushes results into the shared queues.
"""

import subprocess
import queue

import cv2
import numpy as np
from ultralytics import YOLO

from config import (
    FRAME_W, FRAME_H, FRAMERATE,
    WARN_THRESHOLD, TRACK_THRESHOLD,
    warn_queue, track_queue,
)


def _try_put(q: queue.Queue, item):
    """Non-blocking put — drops the oldest item if the queue is full."""
    try:
        q.put_nowait(item)
    except queue.Full:
        try:
            q.get_nowait()
        except queue.Empty:
            pass
        q.put_nowait(item)


def run_DD(weights_path: str):
    print("[DD] Loading YOLO model …")
    model = YOLO(weights_path)

    cmd = [
        "rpicam-vid",
        "--width",     str(FRAME_W),
        "--height",    str(FRAME_H),
        "--framerate", str(FRAMERATE),
        "--codec",     "yuv420",
        "--nopreview",
        "-t", "0",
        "-o", "-",
    ]
    proc       = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    frame_size = FRAME_W * FRAME_H * 3 // 2

    print("[DD] Camera stream started.")

    try:
        while True:
            # ── read & decode frame ───────────────────────────
            raw = proc.stdout.read(frame_size)
            if len(raw) != frame_size:
                print("[DD] Incomplete frame — stopping.")
                break

            yuv   = np.frombuffer(raw, dtype=np.uint8).reshape(
                        (FRAME_H * 3 // 2, FRAME_W))
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)

            # ── YOLO inference ────────────────────────────────
            results   = model(frame, verbose=False)
            best_conf = 0.0
            best_box  = None          # [x1, y1, x2, y2]

            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    if conf > best_conf:
                        best_conf = conf
                        best_box  = box.xyxy[0].tolist()

            # ── annotate & forward ────────────────────────────
            if best_box and best_conf >= WARN_THRESHOLD:
                x1, y1, x2, y2 = [int(v) for v in best_box]
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                color = (0, 0, 255) if best_conf >= TRACK_THRESHOLD else (0, 165, 255)
                label = f"Drone  {best_conf:.0%}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.circle(frame, (cx, cy), 5, color, -1)
                cv2.putText(frame, label, (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # → W
                _try_put(warn_queue, {
                    "confidence": best_conf,
                    "box": best_box,
                })

                # → T  (only when above tracking threshold)
                if best_conf >= TRACK_THRESHOLD:
                    _try_put(track_queue, {
                        "cx": cx,
                        "cy": cy,
                        "confidence": best_conf,
                    })

            cv2.imshow("Drone Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        proc.terminate()
        cv2.destroyAllWindows()
        print("[DD] Stopped.")
