"""Weather data fetching module using Open-Meteo API."""

from datetime import datetime
from typing import Any

import openmeteo_requests  # type: ignore[import]
import pandas as pd  # type: ignore[import]
import pytz  # type: ignore[import]
import requests_cache  # type: ignore[import]
from retry_requests import retry  # type: ignore[import]


def get_weather_data() -> tuple:
    """Fetch weather data from Open-Meteo API.

    Returns: (daily_dict, hourly_dict, current_weather)
    """
    # Setup Open-Meteo client with cache + retry
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # API config
    url = "https://api.open-meteo.com/v1/forecast"
    daily_vars = ["uv_index_max", "sunrise", "sunset"]
    hourly_vars = [
        "temperature_2m", "apparent_temperature", "precipitation_probability",
        "rain", "snowfall", "snow_depth", "showers", "precipitation", "visibility",
    ]
    current_vars = [
        "temperature_2m", "relative_humidity_2m", "apparent_temperature",
        "precipitation", "rain", "showers", "snowfall",
        "cloud_cover", "wind_direction_10m", "wind_speed_10m",
    ]

    params = {
        "latitude": 42.48948,
        "longitude": -83.14465,
        "daily": daily_vars,
        "hourly": hourly_vars,
        "current": current_vars,
        "timezone": "America/New_York",
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
    }

    response = openmeteo.weather_api(url, params=params)[0]

    # --- Current data ---
    current = response.Current()
    current_weather = {
        var: current.Variables(i).Value() for i, var in enumerate(current_vars)
    }
    current_weather["time"] = current.Time()

    # --- Hourly data ---
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
    }
    for i, var in enumerate(hourly_vars):
        hourly_data[var] = hourly.Variables(i).ValuesAsNumpy()
    hourly_dict = pd.DataFrame(hourly_data).to_dict(orient="records")

    # --- Daily data ---
    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left",
        ),
    }
    for i, var in enumerate(daily_vars):
        method = "ValuesInt64AsNumpy" if var in ("sunrise", "sunset") else "ValuesAsNumpy"
        daily_data[var] = getattr(daily.Variables(i), method)()
    daily_dict = pd.DataFrame(daily_data).to_dict(orient="records")

    daily_dict, hourly_dict, current_weather = make_pretty(daily_dict, hourly_dict, current_weather)
    return daily_dict, hourly_dict, current_weather



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
