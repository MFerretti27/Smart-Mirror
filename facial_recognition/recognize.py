"""Face recognition using LBPH and rpicam-still."""

import logging
import pickle
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

import cv2  # type: ignore[import]
import FreeSimpleGUI as Sg  # type: ignore[import]
import numpy as np  # type: ignore[import]

from configuration.settings import DETECTION_THRESHOLD, RECOGNITION_THRESHOLD

logger = logging.getLogger(__name__)

TRAINER_FILE = Path("trainer.yml")
ENCODINGS_FILE = Path("encodings.pkl")
DATASET_DIR = Path("dataset")

def capture_frame(retries: int = 3, delay: float = 1.0) -> Any:
    """Capture a frame using rpicam-still and return as OpenCV image."""
    tmp_file = "/tmp/capture.jpg"

    def raise_capture_error(message: str) -> None:
        raise RuntimeError(message)

    for attempt in range(retries):
        try:
            # Take picture with 2-second exposure to ensure camera is ready
            subprocess.run(
                ["rpicam-still", "-t", "2000", "-n", "-o", tmp_file],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Wait briefly to ensure file is written
            time.sleep(0.2)

            # Load image
            frame = cv2.imread(tmp_file)
            if frame is None:
                raise_capture_error("Failed to read captured image")

        except (subprocess.CalledProcessError, cv2.error, RuntimeError) as e:
            logger.info("Capture attempt %d failed: %s", attempt + 1, e)
            time.sleep(delay)

        return frame

    raise_capture_error("Failed to capture frame after multiple attempts")
    return None  # Unreachable

def train_model() -> None:
    """Train LBPH face recognizer from dataset images."""
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # type: ignore[attr-defined, arg-type]
    faces = []
    labels = []
    label_map = {}
    current_label = 0

    for person in sorted(Path.iterdir(DATASET_DIR)):
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
        msg = "No faces found in dataset to train"
        raise RuntimeError(msg)

    # Train recognizer
    recognizer.train(faces, np.array(labels))
    recognizer.save(str(TRAINER_FILE))

    with Path.open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(label_map, f)
    logger.info("Model trained successfully")

def recognize_faces(window: Sg.Window, stop_event: threading.Event) -> None:
    """Continuously recognize faces using rpicam-still and call callback(name)."""
    logger.info("Starting face recognition...")
    no_faces = 0

    if not TRAINER_FILE.exists() or not ENCODINGS_FILE.exists():
        logger.info("Trainer file or encodings not found. Train first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()  # type: ignore[attr-defined]
    recognizer.read(str(TRAINER_FILE))
    with Path.open(ENCODINGS_FILE, "rb") as f:
        label_map = pickle.load(f)

    face_cascade = cv2.CascadeClassifier("/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml")

    while not stop_event.is_set():
        try:
            frame = capture_frame()
        except (cv2.error, RuntimeError) as e:
            logger.info("Failed to capture frame: %s", e)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        logger.info("Detected %d faces", len(faces))

        # If no faces detected for several frames, notify no recognition
        if len(faces) == 0:
            if no_faces == DETECTION_THRESHOLD:
                window.write_event_value("no_recognition", "")
                no_faces = 0

            no_faces += 1
            continue

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            try:
                label, conf = recognizer.predict(roi)
                name = label_map.get(label, "Unknown")
                logger.info("Found %s with confidence %d", name, conf)
                if conf < RECOGNITION_THRESHOLD:  # threshold for recognition
                    window.write_event_value("recognized_face", name)
                    no_faces = 0
            except cv2.error as e:
                logger.info("Recognition error: %s", e)
                continue
