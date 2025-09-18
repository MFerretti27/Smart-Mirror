"""Layout module for Smart Mirror application."""
import FreeSimpleGUI as Sg  # type: ignore[import]

import settings


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
                           [Sg.ProgressBar(100, key="progress_bar", size=(settings.WINDOW_WIDTH, 20),
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
