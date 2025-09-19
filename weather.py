"""Weather data fetching module using Open-Meteo API."""

import openmeteo_requests  # type: ignore[import]
import pandas as pd  # type: ignore[import]
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

    return daily_dict, hourly_dict, current_weather
