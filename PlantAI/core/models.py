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
    
    def strDetail(self) -> str:
        """Returns a complete description of the datatype plant."""
        return f"[{self.plantId}]:[{self.speciesId}] {self.name} -> {self.location}"

    def strBrief(self) -> str:
        """Returns a brief description of the datatype plant."""
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
    
    def strBrief(self) -> str:
        """Returns a brief description of the datatype channel."""
        if self.plantId == None:
            # don't show plant name if no plant is assigned
            return f"[{self.channelId}] {self.chDescription} -> {self.plantId}"
        else:
            return f"[{self.channelId}] {self.chDescription} -> [{self.plantId}] {self.plantName}"
    
class species:
    """Datatype for plant species."""
    def __init__(self, name: str, minMoisture: float, speciesId: int = 0):
        self.speciesId = speciesId
        self.name = name
        self.minMoisture = minMoisture

    def strDetail(self) -> str:
        """Returns a complete description of the datatype species."""
        return f"[{self.speciesId}] {self.name} -> {self.minMoisture}%"
    
    def strBrief(self) -> str:
        """Returns a brief description of the datatype species."""
        return f"[{self.speciesId}] {self.name}"
    
class measurement:
    """Datatype for moisture and temperature measurements."""
    def __init__(self, plantId: int, moisture: float, temperature: float, minUntilDry: int, timestamp: str, measureId: int = 0):
        self.measureId = measureId
        self.plantId = plantId
        self.moisture = moisture
        self.temperature = temperature
        self.minUntilDry = minUntilDry
        self.timestamp = timestamp
    
    def strDetail(self) -> str:
        """Returns a complete description of the datatype measurement."""
        return f"[{self.measureId}]:[{self.plantId}] -> {self.moisture:.2f}% - {self.temperature:.2f}°C - {self.minUntilDry}min - [{self.timestamp}]"
        