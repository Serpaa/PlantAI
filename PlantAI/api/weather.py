"""
Description:
    Weather and Geocoding API using OpenMeteo and IPinfo.
Author: Tim Grundey
Created: 03.10.2025
"""

import requests

# Open-Meteo Weather API
def getForecast(location: str = None) -> str:
    """
    Returns a weather forecast based on the chosen or current location.
    
    :param location: Location of the forecast, if not provided the current location will be used.
    :type location: str

    :return: Weather forecast.
    :rtype: str
    """
    # Get coordinates for location
    latitude : float; longitude : float; city : str
    if location == None:
        # Get current location using IPinfo
        latitude, longitude, city = getLocation()
    else:
        # Get provided location using geocoding
        latitude, longitude = geocode(location)
        city = location

    # Create URL and send API request
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&forecast_days=2"
        f"&timezone=Europe%2FBerlin"
    )
    response = requests.get(url)

    # Parse data if request was successful
    if response.status_code == 200:
        data = response.json()

        # Dictionary of todays forecast
        today = {
            "date": data["daily"]["time"][0],
            "tmax": round(data["daily"]["temperature_2m_max"][0]),
            "tmin": round(data["daily"]["temperature_2m_min"][0]),
            "rain": round(data["daily"]["precipitation_sum"][0])
        }

        # Dictionary of tomorrows forecast
        tomorrow = {
            "date": data["daily"]["time"][1],
            "tmax": round(data["daily"]["temperature_2m_max"][1]),
            "tmin": round(data["daily"]["temperature_2m_min"][1]),
            "rain": round(data["daily"]["precipitation_sum"][1])
        }

        # Build and return forecast
        forecast = ""
        forecast += f"Weather forecast for {city}:\n"
        forecast += f"Today the {today['date']}:\n"
        forecast += f"Temperature range: {today['tmin']}°C – {today['tmax']}°C, Rain: {today['rain']} mm\n"
        forecast += f"Tomorrow the {tomorrow['date']}:\n"
        forecast += f"Temperature range: {tomorrow['tmin']}°C – {tomorrow['tmax']}°C, Rain: {tomorrow['rain']} mm"
        return forecast
    else:
        raise ConnectionError(f"Forecast - Error retrieving weather data: {response.status_code}")

# Open-Meteo Geocoding API
def geocode(location: str) -> tuple[float, float]:
    """
    Returns latitute and longitude of the chosen location.
    
    :param location: Location to be used.
    :type location: str

    :return: Latitude and longitude of the location.
    :rtype: tuple[float, float]
    """
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
            raise ValueError("Geocoding - Location not found")
    else:
        raise ConnectionError(f"Geocoding - Error retrieving geodata: {response.status_code}")

# IPinfo location API
def getLocation() -> tuple[float, float, str]:
    """
    Returns the current location using IP data.

    :return: Latitude, longitude and name of the city.
    :rtype: tuple[float, float, str]
    """
    # Create URL and send API request
    url = "https://ipinfo.io/json"
    response = requests.get(url)

    # Parse data if request was successful
    if response.status_code == 200:
        data = response.json()

        latitude, longitude = data["loc"].split(",")
        city = data["city"]

        return latitude, longitude, city
    else:
        raise ConnectionError(f"IPinfo - Error retrieving location: {response.status_code}")
    