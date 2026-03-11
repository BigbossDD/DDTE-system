#this code was tested on the pi 5 with the cam  on a basic face detection script
#and the the system worked perfictly 
#

import cv2
import subprocess
import numpy as np

WIDTH = 640
HEIGHT = 480

cmd = [
    "rpicam-vid",
    "--width", str(WIDTH),
    "--height", str(HEIGHT),
    "--framerate", "30",
    "--codec", "yuv420",
    "--nopreview",
    "-t", "0",
    "-o", "-"
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

# Fixed cascade path
face_cascade = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)

frame_size = WIDTH * HEIGHT * 3 // 2

while True:

    raw = proc.stdout.read(frame_size)
    if len(raw) != frame_size:
        break

    yuv = np.frombuffer(raw, dtype=np.uint8).reshape((HEIGHT * 3 // 2, WIDTH))
    frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

    cv2.imshow("Face Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

proc.terminate()
cv2.destroyAllWindows()