"""
DD.py  –  TEMP Detection (Face instead of Drone)
───────────────────────────────────────────────
Uses Haar Cascade for fast face detection on Pi 5.
Keeps same pipeline interface (warn + track queues).
"""

import subprocess
import queue
import cv2
import numpy as np

from config import (
    FRAME_W, FRAME_H, FRAMERATE,
    WARN_THRESHOLD, TRACK_THRESHOLD,
    warn_queue, track_queue,
)


def _try_put(q: queue.Queue, item):
    try:
        q.put_nowait(item)
    except queue.Full:
        try:
            q.get_nowait()
        except queue.Empty:
            pass
        q.put_nowait(item)


def run_DD(_weights_path=None):  # not needed now
    print("[DD] Loading Face Detector …")

    face_cascade = cv2.CascadeClassifier(
        "haarcascade_frontalface_default.xml"
    )

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
            # ── read frame ───────────────────────────
            raw = proc.stdout.read(frame_size)
            if len(raw) != frame_size:
                print("[DD] Incomplete frame — stopping.")
                break

            yuv = np.frombuffer(raw, dtype=np.uint8).reshape(
                (FRAME_H * 3 // 2, FRAME_W)
            )
            frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # ── Face detection ───────────────────────
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5
            )

            best_conf = 0.0
            best_box = None

            for (x, y, w, h) in faces:
                # Fake confidence based on size (relative area)
                area = w * h
                conf = min(1.0, area / (FRAME_W * FRAME_H * 0.25))  # normalize

                if conf > best_conf:
                    best_conf = conf
                    best_box = [x, y, x + w, y + h]

            # ── annotate & forward ───────────────────
            if best_box and best_conf >= WARN_THRESHOLD:
                x1, y1, x2, y2 = [int(v) for v in best_box]
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                color = (0, 0, 255) if best_conf >= TRACK_THRESHOLD else (0, 165, 255)
                label = f"Face {best_conf:.0%}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.circle(frame, (cx, cy), 5, color, -1)
                cv2.putText(frame, label, (x1, y1 - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # → W
                _try_put(warn_queue, {
                    "confidence": best_conf,
                    "box": best_box,
                })

                # → T
                if best_conf >= TRACK_THRESHOLD:
                    _try_put(track_queue, {
                        "cx": cx,
                        "cy": cy,
                        "confidence": best_conf,
                    })

            cv2.imshow("Face Detection (TEMP)", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        proc.terminate()
        cv2.destroyAllWindows()
        print("[DD] Stopped.")