"""Settings for the Smart Mirror."""

import os

import FreeSimpleGUI as Sg  # type: ignore[import]

os.environ["DISPLAY"] = ":0.0"
FONT = "Helvetica"
DATE_TXT_SIZE = 30
QUOTE_TXT_SIZE = 30
GREETING_TXT_SIZE = 60
WINDOW_WIDTH = Sg.Window.get_screen_size()[0]
WINDOW_HEIGHT = Sg.Window.get_screen_size()[1]
BACKGROUND_COLOR = "black"
TEXT_COLOR = "white"
UPDATE_INTERVAL = 600  # 10 minutes in seconds
TIMEZONE = "US/Eastern"
NUM_SAMPLES = 20  # number of images per person
RECOGNITION_THRESHOLD = 120  # lower is more strict
DETECTION_THRESHOLD = 5  # number of consecutive detections to no longer recognize
