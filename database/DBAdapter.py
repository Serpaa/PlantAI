from abc import ABC, abstractmethod
from database.DBConnector import DBConnector
from data.Models import plant, species, sensor, measurement

class DBAdapter(ABC):
    @abstractmethod
    def getList(self):
        pass

    @abstractmethod
    def insert(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

class DBAdapterPlant(DBAdapter):
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def getList(self) -> list[plant]:
        query = "SELECT * FROM plants"
        allPlants = []

        # Create a list of plants
        for entry in self.db_connector.execute(query):
            allPlants.append(plant(plantId=entry[0], speciesId=entry[1], sensorId=entry[2], name=entry[3]))
        return allPlants

    def insert(self, data: plant):
        query = "INSERT INTO plants (speciesId, sensorId, name) VALUES (?, ?, ?)"
        values = (data.speciesId, data.sensorId, data.name)
        self.db_connector.execute(query, values)

    def update(self, data: plant):
        query = "UPDATE plants SET speciesId = ?, sensorId = ?, name = ? WHERE plantId = ?"
        values = (data.speciesId, data.sensorId, data.name, data.plantId)
        self.db_connector.execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM plants WHERE plantId = ?"
        values = (data,)
        self.db_connector.execute(query, values)

class DBAdapterSpecies(DBAdapter):
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def getList(self) -> list[species]:
        query = "SELECT * FROM species"    
        allSpecies = []

        # Create a list of species
        for entry in self.db_connector.execute(query):
            allSpecies.append(species(speciesId=entry[0], name=entry[1]))
        return allSpecies

    def insert(self, data: species):
        query = "INSERT INTO species (name) VALUES (?)"
        values = (data.name,)
        self.db_connector.execute(query, values)

    def update(self, data: species):
        query = "UPDATE species SET name = ? WHERE speciesId = ?"
        values = (data.name, data.speciesId)
        self.db_connector.execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM species WHERE speciesId = ?"
        values = (data,)
        self.db_connector.execute(query, values)

class DBAdapterSensor(DBAdapter):
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def getList(self) -> list[sensor]:
        query = "SELECT * FROM sensors"
        allSensors = []

        # Create a list of sensors
        for entry in self.db_connector.execute(query):
            allSensors.append(sensor(sensorId=entry[0], i2cAddress=entry[1]),)
        return allSensors

    def insert(self, data: sensor):
        query = "INSERT INTO sensors (i2cAddress) VALUES (?)"
        values = (data.i2cAddress,)
        self.db_connector.execute(query, values)

    def update(self, data: sensor):
        query = "UPDATE sensors SET i2cAddress = ? WHERE sensorId = ?"
        values = (data.i2cAddress, data.sensorId)
        self.db_connector.execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM sensors WHERE sensorId = ?"
        values = (data,)
        self.db_connector.execute(query, values)

class DBAdapterMeasurement(DBAdapter):
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def getList(self, where: int, limit: int) -> list[measurement]:
        query = """
        SELECT * FROM (
            SELECT * FROM measurements WHERE sensorId = ? 
            ORDER BY timestamp DESC 
            LIMIT ?) 
        ORDER BY timestamp"""
        values = (where, limit)
        allMeasurements = []

        # Create a list of measurements
        for entry in self.db_connector.execute(query, values):
            allMeasurements.append(measurement(measureId=entry[0], sensorId=entry[1], moisture=entry[2], temperature=entry[3], timestamp=entry[4]))
        return allMeasurements

    def insert(self, data: measurement):
        query = "INSERT INTO measurements (sensorId, moisture, temperature, timestamp) VALUES (?, ?, ?, ?)"
        values = (data.sensorId, data.moisture, data.temperature, data.timestamp)
        self.db_connector.execute(query, values)

    def update(self, data: measurement):
        query = "UPDATE measurements SET sensorId = ?, moisture = ?, temperature = ?, timestamp = ? WHERE measureId = ?"
        values = (data.sensorId, data.moisture, data.temperature, data.timestamp, data.measureId)
        self.db_connector.execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM measurements WHERE measureId = ?"
        values = (data,)
        self.db_connector.execute(query, values)
