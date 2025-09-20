"""Smart Mirror Application."""

from __future__ import annotations

import random
import time
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
import logging
from datetime import date, datetime
from pathlib import Path

import FreeSimpleGUI as Sg  # type: ignore[import]
import pytz  # type: ignore[import]

import settings
from layout import create_weather_layout, update_weather
from quotes import quotes
from records import records

logger = logging.getLogger(__name__)



######################################
# ---------- Quote picker ---------- #
######################################
# remember last 10 picks (indices)
history: deque[int] = deque(maxlen=10)
def pick_index(array_to_pick_from: Sequence[str] | None = None) -> int:
    """Pick an index from array_to_pick_from avoiding recent picks."""
    if array_to_pick_from is None:
        array_to_pick_from = quotes  # use imported quotes

    length = max(1, len(array_to_pick_from))
    # Base weights
    weights = [1.0] * length
    for h in history:
        if 0 <= h < length:
            weights[h] *= 0.3
    index = random.choices(range(length), weights=weights, k=1)[0]
    history.append(index)
    return index

########################################
# ---------- Add new person ---------- #
########################################
def add_new_person(current_quote: str, window: Sg.Window) -> None:
    """Use facial recognition to identify a person and update the welcome message.

    :param current_quote: The current quote being displayed
    :param window: The GUI window to update
    """
    collecting_name = False
    taking_pictures = False
    decide_what_to_display = False
    first_question_asked = False
    name = ""

    while True:
        event, _ = window.read(timeout=100)
        if "Escape" in event:
            window["welcome_message"].update("")
            window["quote_of_day"].update(current_quote)
            return

        # Start entering name
        if not collecting_name and not taking_pictures and not decide_what_to_display:
            window["welcome_message"].update("Enter Name:")
            window["quote_of_day"].update("")
            name = ""
            collecting_name = True
            continue

        # Finish entering name
        if "Return" in event and collecting_name:
            if name == "":
                window["quote_of_day"].update("Name cannot be blank, please enter something or Escape to quit")
            elif name in records:
                window["quote_of_day"].update(f"{name} is already taken, please use another")
            else:
                window["welcome_message"].update(f"Name Recorded:  {name}")
                records[name] = []
                window["quote_of_day"].update("")
                window.read(timeout=100)
                time.sleep(2)
                # create directory for person if desired:
                # with contextlib.suppress(OSError):
                #     (Path.cwd() / "people" / name).mkdir(parents=True, exist_ok=True)
                collecting_name = False
                taking_pictures = True
                window["welcome_message"].update("Press Enter to Start Taking Pictures")
                window["quote_of_day"].update("Please stand ~3 feet away and move slowly to capture angles")
            continue

        # Collect letters while in name entry mode
        if collecting_name:
            if len(event) == 1 and event.isalpha():  # only single characters and letters
                name += event
                window["welcome_message"].update(f"Enter Name:  {name}")
            if "BackSpace" in event or "Delete" in event or "Back" in event:
                name = name[:-1]
                window["welcome_message"].update(f"Enter Name:  {name}")
            continue

        # Start taking pictures
        if "Return" in event and taking_pictures:
            window["welcome_message"].update("Taking Pictures...")
            window["quote_of_day"].update("")
            window["progress_bar"].update(visible=True)

            for i in range(100):
                time.sleep(0.1)
                # TODO(mattFerretti): Take pictures here and save into (Path.cwd()/name)
                window["progress_bar"].update(i + 1)

            window["quote_of_day"].update(current_quote)
            taking_pictures = False
            window["progress_bar"].update(visible=False)

            decide_what_to_display = True
            continue

        # Decide what to display (mean or nice, joke types, etc)
        if decide_what_to_display:
            if not first_question_asked:
                window["welcome_message"].update("Should I be Mean or nice?")
                window["quote_of_day"].update("1: Mean    2: Nice")
            if event == "1" and not first_question_asked:
                window["welcome_message"].update("What jokes to tell?")
                window["quote_of_day"].update("0: Exit   1: Racist   2: Sexist   3: Dad   4: Dark Humor")
                first_question_asked = True
                continue

            if first_question_asked:
                if event == "0":
                    window["welcome_message"].update("")
                    window["quote_of_day"].update(current_quote)
                    try:
                        with Path("records.py").open("w", encoding="utf-8") as f:
                            f.write(f"records = {records}")
                    except OSError:
                        logger.exception("Failed to write to records.py")
                    return

                mapping = {
                    "1": "racist_jokes",
                    "2": "sexist_jokes",
                    "3": "dad_jokes",
                    "4": "dark_humor",
                    "5": "my_quotes",
                }

                if str(event) in mapping:
                    records[name].append(mapping[str(event)])
                    window["welcome_message"].update(f"Added {mapping[str(event)].replace('_', ' ')}, Any more?")
                    event = None
                    continue

            # If user chose '2' (nice path) - add dad_jokes then exit
            if event == "2":
                records[name].append("dad_jokes")
                window["welcome_message"].update("")
                window["quote_of_day"].update(current_quote)
                try:
                    with Path("records.py").open("w", encoding="utf-8") as f:
                        f.write(f"records = {records}")
                except OSError:
                    logger.exception("Failed to write to records.py")
                return


###################################
# ---------- Main loop ---------- #
###################################
def main() -> None:
    """Run the Smart Mirror application."""
    window = Sg.Window(
        "Scoreboard",
        create_weather_layout(),
        no_titlebar=False,
        resizable=True,
        return_keyboard_events=True,
    ).Finalize()

    window.set_cursor("none")  # Hide the mouse cursor
    window.Maximize()

    last_date: date | None = None
    last_update = 0.0
    current_quote = ""

    # initial update (wrapped to not crash if fetch fails)
    try:
        update_weather(window)
    except Exception:
        logger.exception("Initial weather update failed")

    while True:
        event, _ = window.read(timeout=100)
        if event == Sg.WIN_CLOSED or "Escape" in str(event):
            break

        # Update weather at regular intervals
        if time.time() - last_update >= float(settings.UPDATE_INTERVAL):
            try:
                update_weather(window)
            except OSError:
                logger.exception("Weather update failed")
            last_update = time.time()

        # If it's a new day, pick a new random quote
        today = datetime.now(pytz.timezone(settings.TIMEZONE)).date()
        if last_date != today:
            i = pick_index()
            window["quote_of_day"].update(quotes[i])
            current_quote = quotes[i]
            last_date = today

        # TODO(mattFerretti): integrate facial recognition to update the welcome message
        if "Return" in str(event) or event == "Return":
            add_new_person(current_quote, window)

    window.close()


if __name__ == "__main__":
    main()
