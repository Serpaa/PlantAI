"""
Description:
    Data models for all database tables
Author: Tim Grundey
Created: 25.09.2025
"""

class plant:
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
    
class species:
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
        