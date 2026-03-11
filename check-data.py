import os
import cv2
import random

# 🔴 CHANGE THIS PATH
DATASET_PATH = r"C:\Users\USER\OneDrive\Desktop\DDTE-data\Database1\Database1"

print("Checking path:", DATASET_PATH)
print("Path exists:", os.path.exists(DATASET_PATH))

# Get all image files (including jpeg)
image_files = [f for f in os.listdir(DATASET_PATH)
               if f.lower().endswith((".jpg", ".jpeg", ".png"))]

print("Total images found:", len(image_files))

if len(image_files) == 0:
    print("❌ No images found. Check file extensions or path.")
    exit()

random.shuffle(image_files)

for file in image_files[:10]:  # check 10 images
    print("Opening:", file)

    img_path = os.path.join(DATASET_PATH, file)
    label_path = os.path.join(DATASET_PATH,
                              os.path.splitext(file)[0] + ".txt")

    img = cv2.imread(img_path)

    if img is None:
        print("❌ Failed to load:", file)
        continue

    h, w, _ = img.shape

    if os.path.exists(label_path):
        with open(label_path, "r") as f:
            lines = f.readlines()

        if len(lines) == 0:
            print("⚠ EMPTY LABEL:", file)

        for line in lines:
            data = line.strip().split()
            if len(data) != 5:
                continue

            cls, x, y, bw, bh = map(float, data)

            x1 = int((x - bw/2) * w)
            y1 = int((y - bh/2) * h)
            x2 = int((x + bw/2) * w)
            y2 = int((y + bh/2) * h)

            cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
    else:
        print("❌ No label file:", file)

    cv2.imshow("Check", img)

    key = cv2.waitKey(0)
    if key == 27:  # ESC to exit early
        break

cv2.destroyAllWindows()