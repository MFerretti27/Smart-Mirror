"""Layout module for Smart Mirror application."""
import FreeSimpleGUI as Sg  # type: ignore[import]

from configuration import settings
from configuration.settings import NUM_SAMPLES
from weather import get_weather_data


def create_weather_layout() -> list:
    """Create General User Interface.

    :return layout: List of elements and how the should be displayed
    """
    Sg.theme("black")

    weather_week = [
        [Sg.Text("", pad=((0, 0), (0, 20)), font=(settings.FONT, settings.DATE_TXT_SIZE), key="date")],

        [Sg.Text("", pad=((0, 0), (0, 0)), key="sunrise"),
         Sg.Text("", pad=((0, 0), (0, 0)), key="sunset")],

        [Sg.Text("", pad=((0, 0), (0, 0)), key="humidity"),
         Sg.Text("", pad=((0, 0), (0, 0)), key="uv_index")],

        [Sg.Text("", pad=((0, 0), (0, 0)), key="cloud_cover"),
         Sg.Text("", pad=((0, 0), (0, 0)), key="wind")],

        [Sg.Text("", pad=((0, 0), (0, 0)), key="current_temp"),
         Sg.Text("", pad=((0, 0), (0, 0)), key="current_apparent_temp")],

        [Sg.Text("", pad=((0, 0), (0, 0)), key="current_precipitation"),
         Sg.Text("", pad=((0, 0), (0, 0)), key="precipitation_chance")],

        [Sg.VPush()],
        [Sg.Push()],
    ]


    quote_of_day = [[Sg.VPush()],
                     [Sg.Multiline("Quote of the Day", no_scrollbar=True, disabled=True,
                                   size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT * (1 / 8)),
                                   font=(settings.FONT, settings.QUOTE_TXT_SIZE),
                                   background_color=settings.BACKGROUND_COLOR,
                                   border_width=0,
                             justification="center", key="quote_of_day"),
                    ],
                    [Sg.VPush()],
                    ]

    welcome_message = [[Sg.VPush()],
                          [Sg.Push(),
                           Sg.Text("", font=(settings.FONT, settings.GREETING_TXT_SIZE),
                                   key="welcome_message"),
                           Sg.Push()],
                           [Sg.ProgressBar(NUM_SAMPLES, key="progress_bar", size=(settings.WINDOW_WIDTH, 20),
                        bar_color=("green", "white"), visible=False)],
                          [Sg.VPush()],
                          [Sg.Push()],
                          ]

    return [
        [Sg.Frame("", weather_week, element_justification="left", border_width=0, pad=((50, 0), (50, 0)),
                   size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT * (5 / 8)))],

        [Sg.Frame("", welcome_message, element_justification="center", border_width=0,
                  size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT * (1 / 8)))],

        [Sg.Frame("", quote_of_day, element_justification="center", border_width=0,
                  size=(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT * (1 / 8)))],
    ]



################################################
# ---------- Update weather and GUI ---------- #
################################################
def update_weather(window: Sg.Window) -> None:
    """Fetch and update the weather data in the GUI window.

    :param window: The GUI window to update
    """
    daily_dict, hourly_dict, current_weather = get_weather_data()

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
    window["wind"].update(f"Wind: {current_weather.get('wind_speed_10m','')}  "
                          f"{current_weather.get('wind_direction_10m','')}")

    window["humidity"].update(f"Humidity: {current_weather.get('relative_humidity_2m','')}\t")
