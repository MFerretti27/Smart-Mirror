"""Weather data fetching module using Open-Meteo API."""

# Get weather data from: https://open-meteo.com/en/docs?&timezone=America%2FNew_York

import openmeteo_requests  # type: ignore[import]
import pandas as pd  # type: ignore[import]
import requests_cache  # type: ignore[import]
from retry_requests import retry  # type: ignore[import]


def get_weather_data() -> tuple:
    """Fetch weather data from Open-Meteo API.

    return a tuple of weather data (daily_dict, hourly_dict, current_weather)
    """
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession(".cache", expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 42.48948,
        "longitude": -83.14465,
        "daily": ["uv_index_max", "sunrise", "sunset"],
        "hourly": ["temperature_2m", "apparent_temperature", "precipitation_probability", "rain", "snowfall", "snow_depth", "showers", "precipitation", "visibility"],
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "showers", "snowfall", "cloud_cover", "wind_direction_10m", "wind_speed_10m"],
        "timezone": "America/New_York",
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process current data. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature_2m = current.Variables(0).Value()
    current_relative_humidity_2m = current.Variables(1).Value()
    current_apparent_temperature = current.Variables(2).Value()
    current_precipitation = current.Variables(3).Value()
    current_rain = current.Variables(4).Value()
    current_showers = current.Variables(5).Value()
    current_snowfall = current.Variables(6).Value()
    current_cloud_cover = current.Variables(7).Value()
    wind_direction_10m = current.Variables(8).Value()
    wind_speed_10m = current.Variables(9).Value()

    current_weather = {
        "time": current.Time(),
        "temperature_2m": current_temperature_2m,
        "relative_humidity_2m": current_relative_humidity_2m,
        "apparent_temperature": current_apparent_temperature,
        "precipitation": current_precipitation,
        "rain": current_rain,
        "showers": current_showers,
        "snowfall": current_snowfall,
        "cloud_cover": current_cloud_cover,
        "wind_direction_10m": wind_direction_10m,
        "wind_speed_10m": wind_speed_10m,
    }

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
    hourly_rain = hourly.Variables(3).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(4).ValuesAsNumpy()
    hourly_snow_depth = hourly.Variables(5).ValuesAsNumpy()
    hourly_showers = hourly.Variables(6).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(7).ValuesAsNumpy()
    hourly_visibility = hourly.Variables(8).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left",
        )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["apparent_temperature"] = hourly_apparent_temperature
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["rain"] = hourly_rain
    hourly_data["snowfall"] = hourly_snowfall
    hourly_data["snow_depth"] = hourly_snow_depth
    hourly_data["showers"] = hourly_showers
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["visibility"] = hourly_visibility

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    hourly_dict = hourly_dataframe.to_dict(orient="records")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_uv_index_max = daily.Variables(0).ValuesAsNumpy()
    daily_sunrise = daily.Variables(1).ValuesInt64AsNumpy()
    daily_sunset = daily.Variables(2).ValuesInt64AsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left",
        )}

    daily_data["uv_index_max"] = daily_uv_index_max
    daily_data["sunrise"] = daily_sunrise
    daily_data["sunset"] = daily_sunset

    daily_dataframe = pd.DataFrame(data = daily_data)
    daily_dict = daily_dataframe.to_dict(orient="records")

    return daily_dict, hourly_dict, current_weather
