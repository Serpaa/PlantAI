"""
Description:
    Data models for all database tables
Author: Tim Grundey
Created: 25.09.2025
"""

class plant:
    def __init__(self, name: str, speciesId: int, sensorId: int, plantId: int = 0):
        self.plantId = plantId
        self.speciesId = speciesId
        self.sensorId = sensorId
        self.name = name
    
    def __str__(self) -> str:
        return f"[{self.plantId} | {self.speciesId} | {self.sensorId} | {self.name}]"
    
class species:
    def __init__(self, name: str, minMoisture: float, speciesId: int = 0):
        self.speciesId = speciesId
        self.name = name
        self.minMoisture = minMoisture

    def __str__(self) -> str:
        return f"[{self.speciesId} | {self.name} | {self.minMoisture}]"

class sensor:
    def __init__(self, i2cAddress : int, sensorId: int = 0):
        self.sensorId = sensorId
        self.i2cAddress = i2cAddress

    def __str__(self) -> str:
        return f"[{self.sensorId} | {self.i2cAddress}]"
    
class measurement:
    def __init__(self, sensorId: int, moisture: float, temperature: float, minUntilDry: int, timestamp: str, measureId: int = 0):
        self.measureId = measureId
        self.sensorId = sensorId
        self.moisture = moisture
        self.temperature = temperature
        self.minUntilDry = minUntilDry
        self.timestamp = timestamp
    
    def __str__(self) -> str:
        return f"[{self.measureId} | {self.sensorId} | {self.moisture:.2f} | {self.temperature:.2f} | {self.minUntilDry} | {self.timestamp}]"
        