"""Face recognition using LBPH and rpicam-still."""

import os
import time
import pickle
from pathlib import Path
import threading
import subprocess
import numpy as np
import FreeSimpleGUI as Sg  # type: ignore[import]

import cv2

TRAINER_FILE = Path("trainer.yml")
ENCODINGS_FILE = Path("encodings.pkl")
DATASET_DIR = Path("dataset")

def capture_frame(retries=3, delay=1.0):
    """Capture a frame using rpicam-still and return as OpenCV image."""
    tmp_file = "/tmp/capture.jpg"
    for attempt in range(retries):
        try:
            # Take picture with 2-second exposure to ensure camera is ready
            subprocess.run(
                ["rpicam-still", "-t", "2000", "-n", "-o", tmp_file],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Wait briefly to ensure file is written
            time.sleep(0.2)

            # Load image
            frame = cv2.imread(tmp_file)
            if frame is None:
                raise RuntimeError("Failed to read captured image")
            return frame
        except Exception as e:
            print(f"Capture attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise RuntimeError("Failed to capture frame after multiple attempts")

def train_model() -> None:
    """Train LBPH face recognizer from dataset images."""
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []
    label_map = {}
    current_label = 0

    for person in sorted(os.listdir(DATASET_DIR)):
        person_dir = DATASET_DIR / person
        if not person_dir.is_dir():
            continue
        for img_file in person_dir.glob("*.jpg"):
            img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            # Resize to fixed size
            img = cv2.resize(img, (200, 200))
            faces.append(img.astype(np.uint8))
            labels.append(current_label)
        label_map[current_label] = person
        current_label += 1

    if not faces:
        raise RuntimeError("No faces found in dataset to train")

    # Train recognizer
    recognizer.train(faces, np.array(labels))
    recognizer.save(str(TRAINER_FILE))

    with open(ENCODINGS_FILE, "wb") as f:
        import pickle
        pickle.dump(label_map, f)
    print("Model trained successfully")

def recognize_faces(window: Sg.Window, stop_event: threading.Event) -> None:
    """Continuously recognize faces using rpicam-still and call callback(name)."""
    print("Starting face recognition...")
    no_faces = 0

    if not TRAINER_FILE.exists() or not ENCODINGS_FILE.exists():
        print("Trainer file or encodings not found. Train first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(TRAINER_FILE))
    with open(ENCODINGS_FILE, "rb") as f:
        label_map = pickle.load(f)

    face_cascade = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")

    while not stop_event.is_set():
        try:
            frame = capture_frame()
        except Exception as e:
            print(f"Failed to capture frame: {e}")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        print(f"Detected {len(faces)} faces")

        # If no faces detected for several frames, notify no recognition
        if len(faces) == 0:
            if no_faces == 5:
                window.write_event_value("no_recognition", "")
                no_faces = 0

            no_faces += 1
            continue

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            try:
                label, conf = recognizer.predict(roi)
                name = label_map.get(label, "Unknown")
                print(f"Found {name} with confidence {conf}")
                if conf < 120:  # threshold for recognition
                    window.write_event_value("recognized_face", name)
                    no_faces = 0
            except Exception as e:
                print(f"Recognition error: {e}")
                continue
