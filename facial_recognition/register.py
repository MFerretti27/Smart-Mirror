"""Register new persons and capture face dataset using rpicam-still."""

import logging
import subprocess
from pathlib import Path

import cv2  # type: ignore[import]
import FreeSimpleGUI as Sg  # type: ignore[import]

from settings import NUM_SAMPLES

logger = logging.getLogger(__name__)

# Paths
DATASET_DIR = Path("dataset")
TRAINER_FILE = Path("trainer.yml")
ENCODINGS_FILE = Path("encodings.pkl")

def get_haar_cascade() -> cv2.CascadeClassifier:
    """Return the frontal face Haar cascade."""
    # Try default OpenCV path
    possible = [
        "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
        "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml",
    ]
    for path in possible:
        if Path(path).exists():
            return cv2.CascadeClassifier(str(path))
    msg = "Could not find haarcascade_frontalface_default.xml on system"
    raise FileNotFoundError(msg)

def register_person(window: Sg.Window, name: str) -> None:
    """Capture face images for a new person and save in dataset."""
    window["progress_bar"].update(visible=True)

    person_dir = DATASET_DIR / name
    person_dir.mkdir(parents=True, exist_ok=True)

    face_cascade = get_haar_cascade()
    logger.info("Capturing %d images for %s...", NUM_SAMPLES, name)
    i = 0

    while i < NUM_SAMPLES:
        window.read(timeout=100)
        filename = person_dir / f"{name}_{i}.jpg"
        cmd = f"rpicam-still -o {filename} -t 500 -n"
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            shell=True,
        )
        logger.info("Captured %s", filename)

        # Verify face detection
        img = cv2.imread(str(filename), cv2.IMREAD_GRAYSCALE)
        faces = face_cascade.detectMultiScale(img, 1.3, 5)    # type: ignore[attr-defined, arg-type]
        if len(faces) == 0:
            logger.info("No face detected in %s, retrying...", filename)
            window["quote_of_day"].update("No face detected, retrying...")
        else:
            logger.info("Face detected in %s", filename)
            window["progress_bar"].update(i + 1)
            window["quote_of_day"].update("")
            i += 1

    logger.info("Finished capturing for %s", name)
