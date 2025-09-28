"""Smart Mirror Application with Face Recognition using rpicam-still."""

import contextlib
import logging
import os
import random
import re
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import FreeSimpleGUI as Sg  # type: ignore[import]
import pytz  # type: ignore[import]

import settings
from facial_recognition.recognize import recognize_faces, train_model
from facial_recognition.register import register_person
from layout import create_weather_layout, update_weather
from quotes import dad_jokes, dark_humor, my_quotes, quotes, racist_jokes, sexist_jokes
from records import records

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # or DEBUG if you want more detail
    format="%(message)s"
)

# History for quote picking
history: deque[int] = deque(maxlen=20)

# Types of greeting messages
GREETING_MESSAGES = [
    "Hello",
    "Welcome",
    "Hi",
    "Good to see you",
    "Hey there",
    "Greetings",
    "Salutations",
    "Howdy",
    "Ahoy",
    "Yo",
    "What's up",
    "Good day",
    "Namaste",
]


def pick_index(array_to_pick_from: list[str] = quotes) -> int:
    """Pick an index from array avoiding recent picks."""
    if array_to_pick_from is None:
        array_to_pick_from = quotes
    length = max(1, len(array_to_pick_from))
    weights = [1.0] * length
    for h in history:
        if 0 <= h < length:
            weights[h] *= 0.3
    index = random.choices(range(length), weights=weights, k=1)[0]
    history.append(index)
    return index

def choose_what_to_display(window: Sg.Window, name: str) -> None:
    """Ask user what type of content to display via GUI."""
    first_question_asked = False

    if name not in records:
        records[name] = []

    while True:
        event, _ = window.read(timeout=100)

        event_clean = str(event.split(":")[0]).replace(" ", "") if ":" in str(event) else event

        if not first_question_asked:
            window["welcome_message"].update("Should I be Mean or Nice?")
            window["quote_of_day"].update("1: Mean    2: Nice")
        if event_clean == "1" and not first_question_asked:
            window["welcome_message"].update("What jokes to tell?")
            window["quote_of_day"].update("0: Exit   1: Racist   2: Sexist   3: Dad   4: Dark Humor")
            first_question_asked = True
            continue

        if first_question_asked:
            if event_clean == "0":
                break

            mapping = {
                "1": "racist_jokes",
                "2": "sexist_jokes",
                "3": "dad_jokes",
                "4": "dark_humor",
                "5": "my_quotes",
            }

            if str(event_clean) in mapping:
                records[name].append(mapping[str(event_clean)])
                window["welcome_message"].update(f"Added {mapping[str(event_clean)].replace('_', ' ')}, Any more?")
                event = None
                continue

        # If user chose '2' (nice path) - add dad_jokes then exit
        if event_clean == "2"  and not first_question_asked:
            records[name].append("dad_jokes")
            break

    window["welcome_message"].update("")
    try:
        with Path("records.py").open("w", encoding="utf-8") as f:
            f.write(f"records = {records}")
    except OSError:
        logger.exception("Failed to write to records.py")


def display_joke(window: Sg.Window, name_recognized: str) -> None:
    """Display a joke or quote based on the recognized person's preferences."""
    random_number = random.randint(1, len(records[name_recognized]) - 1)
    chosen_type_of_jokes = records[name_recognized][random_number]

    random_number = random.randint(1, len(GREETING_MESSAGES) - 1)
    greeting_message = GREETING_MESSAGES[random_number]

    lists_map = {
        "racist_jokes": racist_jokes,
        "sexist_jokes": sexist_jokes,
        "dad_jokes": dad_jokes,
        "dark_humor": dark_humor,
        "my_quotes": my_quotes,
    }
    chosen_list_of_jokes = lists_map.get(chosen_type_of_jokes, [])

    window["welcome_message"].update(f"{greeting_message}, {name_recognized}!")
    i = pick_index(chosen_list_of_jokes)
    window["quote_of_day"].update(chosen_list_of_jokes[i])

def collect_name(window: Sg.Window) -> str:
    """Collect name input from GUI."""
    name = ""

    while True:
        event, _ = window.read(timeout=100)
        event_clean = event.replace(":", "")
        event_clean = re.sub(r"\d", "", event_clean)

        if len(event_clean) == 1 and event_clean.isalpha():
            name += event_clean
            window["welcome_message"].update(f"Enter Name: {name}")
        if "BackSpace" in event or "Delete" in event:
            name = name[:-1]
            window["welcome_message"].update(f"Enter Name: {name}")

        if "Return" in event:
            if not name:
                window["quote_of_day"].update("Name cannot be blank")
            elif ((Path("dataset") / name).exists() and (Path("dataset") / name).is_dir()) or name in records:
                window["quote_of_day"].update(f"{name} is already taken, please use another")
            else:
                return name

def add_new_person(current_quote: str, window: Sg.Window) -> None:
    """Register a new person via GUI input."""
    collecting_name = False

    while True:
        event, _ = window.read(timeout=100)
        if event == Sg.WIN_CLOSED or "Escape" in str(event):
            window["welcome_message"].update("")
            window["quote_of_day"].update(current_quote)
            return

        if not collecting_name:
            window["welcome_message"].update("Enter Name:")
            window["quote_of_day"].update("")
            collecting_name = True
            name = collect_name(window)
            window["welcome_message"].update("Press Enter to Start Taking Pictures")
            window["quote_of_day"].update("Please stand ~3 feet away and move slowly to capture angles")
            continue

        if collecting_name and "Return" in event:
            try:
                window["welcome_message"].update("Taking Pictures...")
                window["quote_of_day"].update("")
                window.refresh()
                register_person(window, name)  # Capture images using rpicam-still
                train_model()  # Rebuild LBPH model
                window["welcome_message"].update("Successfully Registered!")
                window["progress_bar"].update(visible=False)
                window.refresh()
                time.sleep(2)
                choose_what_to_display(window, name)
            except Exception:
                logger.exception("Error registering new person")
                window["quote_of_day"].update(f"Error registering {name}")
                return

            window["welcome_message"].update("")
            window["quote_of_day"].update(current_quote)
            return

def change_person_preferences(window: Sg.Window, name: str) -> None:
    """Change preferences for an existing person."""
    window["welcome_message"].update("Change Person's Preferences")

    while True:
        event, _ = window.read(timeout=100)
        if event == Sg.WIN_CLOSED or "Escape" in str(event):
            break

        event_clean = event.replace(":", "")
        event_clean = re.sub(r"\d", "", event_clean)

        if len(event_clean) == 1 and event_clean.isalpha():
            name += event_clean
            window["welcome_message"].update(f"Enter Name: {name}")
        if "BackSpace" in event or "Delete" in event:
            name = name[:-1]
            window["welcome_message"].update(f"Enter Name: {name}")

        if "Return" in event or "Enter" in event:
            window["welcome_message"].update(f"Enter Name: {name}")

            if name not in records:
                window["quote_of_day"].update("Person not found. Press Shift to list all people registered.")

            else:
                records[name] = []
                choose_what_to_display(window, name)

def main() -> None:
    """Run the Smart Mirror application."""
    os.environ["DISPLAY"] = ":0.0"

    window = Sg.Window(
        "Smart Mirror",
        create_weather_layout(),
        no_titlebar=False,
        resizable=True,
        return_keyboard_events=True,
    ).Finalize()

    window.set_cursor("none")
    window.Maximize()

    last_date = None
    last_update = 0.0
    current_quote = ""
    name_already_detected = False

    # Initial weather update
    with contextlib.suppress(Exception):
        update_weather(window)

    # Start recognition thread
    recog_stop = threading.Event()
    recog_thread = threading.Thread(target=recognize_faces, args=(window, recog_stop), daemon=True)
    recog_thread.start()

    while True:
        event, values = window.read(timeout=100)
        if event == Sg.WIN_CLOSED or "Escape" in str(event):
            break

        # Update weather periodically
        if time.time() - last_update >= float(settings.UPDATE_INTERVAL):
            with contextlib.suppress(Exception):
                update_weather(window)
            last_update = time.time()

        # Update daily quote
        today = datetime.now(pytz.timezone(settings.TIMEZONE)).date()
        if last_date != today:
            i = pick_index()
            window["quote_of_day"].update(quotes[i])
            current_quote = quotes[i]
            last_date = today

        # Handle recognized faces
        if event == "recognized_face":
            logger.info("Face event detected!")
            name_recognized = values.get("recognized_face")
            if name_recognized and not name_already_detected:
                name_already_detected = True
                display_joke(window, name_recognized)

        # Handle no recognition
        if event == "no_recognition":
            name_already_detected = False
            logger.info("No face recognized.")
            window["quote_of_day"].update(current_quote)
            window["welcome_message"].update("")

        # Add new person
        if "Return" in str(event) or event == "Enter":
            add_new_person(current_quote, window)
            recog_thread.start()

    recog_stop.set()
    recog_thread.join(timeout=1.0)
    window.close()


if __name__ == "__main__":
    main()
