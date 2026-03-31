"""
Description:
    Data models for all database tables
Author: Tim Grundey
Created: 25.09.2025
"""

class plant:
    """Datatype for plants."""
    def __init__(self, name: str, location: str, speciesId: int, plantId: int = 0):
        self.plantId = plantId
        self.speciesId = speciesId
        self.name = name
        self.location = location

    def __str__(self) -> str:
        return f"[{self.plantId}] {self.name}"
    
class channel:
    """Datatype for input channels and their assigned plants."""
    def __init__(self, channelId: int, chMoisture: int, chTemperature: int, chDescription: str, plantId: int, plantName: str):
        self.channelId = channelId
        self.chMoisture = chMoisture
        self.chTemperature = chTemperature
        self.chDescription = chDescription
        self.plantId = plantId
        self.plantName = plantName
    
class species:
    """Datatype for plant species."""
    def __init__(self, name: str, minMoisture: float, speciesId: int = 0):
        self.speciesId = speciesId
        self.name = name
        self.minMoisture = minMoisture
    
    def __str__(self) -> str:
        return f"[{self.speciesId}] {self.name}"
    
class measurement:
    """Datatype for moisture and temperature measurements."""
    def __init__(self, plantId: int, moisture: float, temperature: float, minUntilDry: int, isDry: int, timestamp: str, measureId: int = 0):
        self.measureId = measureId
        self.plantId = plantId
        self.moisture = moisture
        self.temperature = temperature
        self.minUntilDry = minUntilDry
        self.isDry = isDry
        self.timestamp = timestamp
