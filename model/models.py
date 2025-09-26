class plant:
    def __init__(self, name: str, species: int, sensor: int, plant_id: int = 0):
        self.plant_id = plant_id
        self.name = name
        self.species = species
        self.sensor = sensor
    
class species:
    def __init__(self, species_id: int, name: str):
        self.species_id = species_id
        self.name = name

class sensor:
    def __init__(self, sensor_id: int, serial_no: str):
        self.sensor_id = sensor_id
        self.serial_no = serial_no

class moisture:
    def __init__(self, moisture_id: int, plant: int, value: float, timestamp: str):
        self.moisture_id = moisture_id
        self.plant = plant
        self.value = value
        self.timestamp = timestamp
        