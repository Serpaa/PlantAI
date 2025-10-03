import requests
from geopy.distance import geodesic

class OpenMeteo:
    # Open-Meteo Weather API
    def getWeather(self, location: str):
        # Get coordinates for location
        latitude : float; longitude : float
        latitude, longitude = self.geocode(location)

        # Create URL and send API request
        url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
            f"&hourly=temperature_2m,relative_humidity_2m,precipitation"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&timezone=Europe%2FBerlin")
        response = requests.get(url)

        # Parse data if request was successful
        forecast = ""
        if response.status_code == 200:
            data = response.json()
            forecast += "Aktuelle Vorhersage:\n"
            forecast += f"  Stündliche Temperaturen (°C): {data['hourly']['temperature_2m'][:5]}\n"
            forecast += f"  Luftfeuchtigkeit (%): {data['hourly']['relative_humidity_2m'][:5]}\n"
            forecast += f"  Niederschlag (mm): {data['hourly']['precipitation'][:5]}\n"
            forecast += "Tagesvorhersage:\n"
            for date, tmax, tmin, rain in zip(
                data["daily"]["time"],
                data["daily"]["temperature_2m_max"],
                data["daily"]["temperature_2m_min"],
                data["daily"]["precipitation_sum"],
            ):
                forecast += f"{date}: {tmin}°C – {tmax}°C, Regen: {rain} mm\n"
        else:
            raise ConnectionError(f"Fehler beim Abrufen der Wetterdaten: {response.status_code}")
        return forecast

    # Open-Meteo Geocoding API
    def geocode(self, location: str):
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
                raise ValueError("Ort nicht gefunden")
        else:
            raise ConnectionError(f"Fehler beim Abrufen der Geodaten: {response.status_code}")
