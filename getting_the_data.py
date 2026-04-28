import os
import shutil
import random
from pathlib import Path

# -------------------------
# CHANGE THIS PATH
# -------------------------
SOURCE_DIR = r"C:\Users\USER\OneDrive\Desktop\DDTE-data\Database1\Database1"
OUTPUT_DIR = r"C:\Users\USER\OneDrive\Desktop\drone_dataset"

# -------------------------
# Create YOLOv8 Structure
# -------------------------
images_train = Path(OUTPUT_DIR) / "images/train"
images_val = Path(OUTPUT_DIR) / "images/val"
labels_train = Path(OUTPUT_DIR) / "labels/train"
labels_val = Path(OUTPUT_DIR) / "labels/val"

for folder in [images_train, images_val, labels_train, labels_val]:
    folder.mkdir(parents=True, exist_ok=True)

# -------------------------
# Get all images
# -------------------------
image_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith((".jpg", ".png"))]

random.shuffle(image_files)

split_ratio = 0.8
split_index = int(len(image_files) * split_ratio)

train_files = image_files[:split_index]
val_files = image_files[split_index:]

# -------------------------
# Move files
# -------------------------
def move_files(file_list, img_dest, lbl_dest):
    for file in file_list:
        img_src = Path(SOURCE_DIR) / file
        lbl_src = Path(SOURCE_DIR) / file.replace(".jpg", ".txt").replace(".png", ".txt")

        shutil.copy(img_src, img_dest / file)

        if lbl_src.exists():
            shutil.copy(lbl_src, lbl_dest / lbl_src.name)
        else:
            # create empty label file if missing
            open(lbl_dest / lbl_src.name, 'w').close()

move_files(train_files, images_train, labels_train)
move_files(val_files, images_val, labels_val)

print("Dataset prepared successfully.")