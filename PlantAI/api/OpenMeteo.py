"""
Description:
    Weather and Geocoding API using OpenMeteo
Author: Tim Grundey
Created: 03.10.2025
"""

import requests
from geopy.distance import geodesic

# Open-Meteo Weather API
def getWeather(location: str):
    """Returns a current weather forecast based on the chosen location."""
    # Get coordinates for location
    latitude : float; longitude : float
    latitude, longitude = geocode(location)

    # Create URL and send API request
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m,precipitation"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=Europe%2FBerlin")
    response = requests.get(url)

    # Parse data if request was successful
    forecast = ""
    if response.status_code == 200:
        data = response.json()
        forecast += f"Current forecast (hourly):\n"
        forecast += f"--------------------\n"
        forecast += f"> Hourly temperatures (in °C):\n"
        forecast += f"  {data['hourly']['temperature_2m'][:6]}\n\n"
        forecast += f"> Rainfall (in mm):\n"
        forecast += f"  {data['hourly']['precipitation'][:6]}\n\n"
        forecast += f"Daily forecast:\n"
        forecast += f"----------------\n"
        for date, tmax, tmin, rain in zip(
            data["daily"]["time"],
            data["daily"]["temperature_2m_max"],
            data["daily"]["temperature_2m_min"],
            data["daily"]["precipitation_sum"],
        ):
            forecast += f"{date}: {tmin}°C – {tmax}°C, Rain: {rain} mm\n"
    else:
        raise ConnectionError(f"Error retrieving weather data: {response.status_code}")
    return forecast

# Open-Meteo Geocoding API
def geocode(location: str):
    """Returns latitute and longitude based on the chosen location."""
    # Create URL and send API request
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=de"
    response = requests.get(url)

    # Parse data if request was successful
    if response.status_code == 200:
        data = response.json()
        # Check if data contains a result
        if "results" in data and len(data["results"]) > 0:  
            latitude = data["results"][0]["latitude"]
            longitude = data["results"][0]["longitude"]
            return latitude, longitude
        else:
            raise ValueError("Location not found")
    else:
        raise ConnectionError(f"Error retrieving geodata: {response.status_code}")
