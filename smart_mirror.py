"""Smart Mirror Application."""

from __future__ import annotations

import random
import time
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import FreeSimpleGUI as Sg  # type: ignore[import]
import pytz  # type: ignore[import]

import settings
from layout import create_weather_layout
from quotes import quotes
from records import records
from weather import get_weather_data as fetch_weather_data

logger = logging.getLogger(__name__)

def make_pretty(
    daily_dict: list[dict[str, Any]],
    hourly_dict: list[dict[str, Any]],
    current_weather: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Make the weather data more human readable.

    :param daily_dict: Daily weather data
    :param hourly_dict: Hourly weather data
    :param current_weather: Current weather data
    :return: Tuple of (daily_dict, hourly_dict, current_weather) with formatted values
    """
    eastern = pytz.timezone("US/Eastern")

    # Format daily data
    for day in daily_dict:
        eastern = pytz.timezone("US/Eastern")

        # Convert directly to 12-hour format without seconds
        sunrise_str = datetime.fromtimestamp(day["sunrise"], eastern).strftime("%-I:%M %p")
        sunset_str  = datetime.fromtimestamp(day["sunset"],  eastern).strftime("%-I:%M %p")

        day["sunrise"] = sunrise_str
        day["sunset"] = sunset_str
        day["date"] = day["date"].strftime("%A, %B %d")
        daily_dict[0]["uv_index_max"] = f"{int(daily_dict[0]['uv_index_max'])}"

    for hour in hourly_dict:
        hour["temperature_2m"] = f"{int(hour['temperature_2m'])} °F"
        hour["apparent_temperature"] = f"{int(hour['apparent_temperature'])} °F"
        hour["precipitation_probability"] = f"{hour['precipitation_probability']}%"
        hour["rain"] = f"{hour['rain']}in"
        hour["snowfall"] = f"{hour['snowfall']}in"
        hour["snow_depth"] = f"{hour['snow_depth']}in"
        hour["showers"] = f"{hour['showers']}in"
        hour["precipitation"] = f"{hour['precipitation']}in"
        hour["visibility"] = f"{hour['visibility']}m"

    # Directions array and wind direction index safe computation
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    wind_direction_index = int((current_weather["wind_direction_10m"] + 11.25) / 22.5) % 16

    current_weather["temperature_2m"] = f"{int(current_weather['temperature_2m'])} °F"
    current_weather["relative_humidity_2m"] = f"{current_weather['relative_humidity_2m']}%"
    current_weather["apparent_temperature"] = f"{int(current_weather['apparent_temperature'])} °F"
    current_weather["precipitation"] = f"{current_weather['precipitation']}in"
    current_weather["rain"] = f"{current_weather['rain']}in"
    current_weather["showers"] = f"{current_weather['showers']}in"
    current_weather["snowfall"] = f"{current_weather['snowfall']}in"
    current_weather["cloud_cover"] = f"{current_weather['cloud_cover']}%"
    current_weather["wind_direction_10m"] = f"{directions[wind_direction_index]}"
    current_weather["wind_speed_10m"] = f"{int(current_weather['wind_speed_10m'])}mph"


    # Convert to datetime
    dt = datetime.fromtimestamp(current_weather["time"], eastern)
    time_str = dt.strftime("%-I:%M %p")  # Format: H:MM (no leading zero, no seconds)
    current_weather["time"] = time_str

    return daily_dict, hourly_dict, current_weather


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


################################################
# ---------- Update weather and GUI ---------- #
################################################
def update_weather(window: Sg.Window) -> None:
    """Fetch and update the weather data in the GUI window.

    :param window: The GUI window to update
    """
    daily_dict, hourly_dict, current_weather = fetch_weather_data()
    daily_dict, hourly_dict, current_weather = make_pretty(daily_dict, hourly_dict, current_weather)

    # Choose which to display rain or snow
    if hourly_dict:
        if current_weather.get("rain", "0") >= current_weather.get("snowfall", "0"):
            window["current_precipitation"].update(f"Current Precipitation: {hourly_dict[0].get('precipitation','')}\t")
            window["precipitation_chance"].update("Precipitation Chance:"
                                                  f"{hourly_dict[0].get('precipitation_probability','')}")
        else:
            window["current_precipitation"].update(f"Next Hour Snowfall: {hourly_dict[0].get('snowfall','')}\t")
            window["precipitation_chance"].update(f"Current Snow Depth: {hourly_dict[0].get('snow_depth','')}")
    else:
        window["current_precipitation"].update("No hourly data")
        window["precipitation_chance"].update("")

    window["date"].update(f"{daily_dict[0].get('date','')}" if daily_dict else "")
    window["current_temp"].update(f"Current Temperature: {current_weather.get('temperature_2m','')}\t")
    window["current_apparent_temp"].update("Current Apparent Temperature:"
                                           f"{current_weather.get('apparent_temperature','')}\t")

    if daily_dict:
        window["sunrise"].update(f"Sunrise: {daily_dict[0].get('sunrise','')}\t")
        window["sunset"].update(f"Sunset: {daily_dict[0].get('sunset','')}")
        window["uv_index"].update(f"UV Index: {daily_dict[0].get('uv_index_max','')}")
    else:
        window["sunrise"].update("")
        window["sunset"].update("")
        window["uv_index"].update("")

    window["cloud_cover"].update(f"Cloud Cover: {current_weather.get('cloud_cover','')}\t")
    window["wind"].update(f"Wind: {current_weather.get('wind_speed_10m','')}"
                          f"{current_weather.get('wind_direction_10m','')}")

    window["humidity"].update(f"Humidity: {current_weather.get('relative_humidity_2m','')}\t")


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
            if "BackSpace" in event or "Delete" in event:
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

    last_date: datetime.date | None = None
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
        try:
            today = datetime.now(pytz.timezone(settings.TIMEZONE)).date()
            if last_date != today:
                i = pick_index()
                window["quote_of_day"].update(quotes[i])
                current_quote = quotes[i]
                last_date = today
        except (ValueError, KeyError, OSError):
            logger.exception("Error updating quote of the day or handling timezone")

        # TODO(mattFerretti): integrate facial recognition to update the welcome message
        if "Return" in str(event) or event == "Return":
            add_new_person(current_quote, window)

    window.close()


if __name__ == "__main__":
    main()
