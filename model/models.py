class plant:
    def __init__(self, name: str, speciesId: int, sensorId: int, plantId: int = 0):
        self.plantId = plantId
        self.speciesId = speciesId
        self.sensorId = sensorId
        self.name = name
    
    def __str__(self) -> str:
        return f"[{self.plantId} | {self.speciesId} | {self.sensorId} | {self.name}]"
    
class species:
    def __init__(self, name: str, speciesId: int = 0):
        self.speciesId = speciesId
        self.name = name

    def __str__(self) -> str:
        return f"[{self.speciesId} | {self.name}]"

class sensor:
    def __init__(self, i2cAddress : int, sensorId: int = 0):
        self.sensorId = sensorId
        self.i2cAddress = i2cAddress

    def __str__(self) -> str:
        return f"[{self.sensorId} | {self.i2cAddress}]"
    
class measurement:
    def __init__(self, sensorId: int, moisture: float, temperature: float, timestamp: str, measureId: int = 0):
        self.measureId = measureId
        self.sensorId = sensorId
        self.moisture = moisture
        self.temperature = temperature
        self.timestamp = timestamp
    
    def __str__(self) -> str:
        return f"[{self.measureId} | {self.sensorId} | {self.moisture} | {self.temperature} | {self.timestamp}]"
        