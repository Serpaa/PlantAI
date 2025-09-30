from abc import ABC, abstractmethod
from database.DBConnector import DBConnector
from model.models import plant, species, sensor, moisture

class DBAdapter(ABC):
    @abstractmethod
    def select(self):
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

    def select(self):
        query = "SELECT * FROM plants"
        return self.db_connector.execute(query)

    def insert(self, data: plant):
        query = "INSERT INTO plants (name, species, sensor) VALUES (?, ?, ?)"
        values = (data.name, data.species, data.sensor)
        self.db_connector.execute(query, values)

    def update(self, data: plant):
        query = "UPDATE plants SET name = ?, species = ?, sensor = ? WHERE plant_id = ?"
        values = (data.name, data.species, data.sensor, data.plant_id)
        self.db_connector.execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM plants WHERE plant_id = ?"
        values = (data,)
        self.db_connector.execute(query, values)

class DBAdapterSpecies(DBAdapter):
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def select(self):
        query = "SELECT * FROM species"
        return self.db_connector.execute(query)

    def insert(self, data: species):
        query = "INSERT INTO species (name) VALUES (?)"
        values = (data.name,)
        self.db_connector.execute(query, values)

    def update(self, data: species):
        query = "UPDATE species SET name = ? WHERE species_id = ?"
        values = (data.name, data.species_id)
        self.db_connector.execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM species WHERE species_id = ?"
        values = (data,)
        self.db_connector.execute(query, values)

class DBAdapterSensor(DBAdapter):
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def select(self):
        query = "SELECT * FROM sensors"
        return self.db_connector.execute(query)

    def insert(self, data: sensor):
        query = "INSERT INTO sensors (serial_no) VALUES (?)"
        values = (data.serial_no,)
        self.db_connector.execute(query, values)

    def update(self, data: sensor):
        query = "UPDATE sensors SET serial_no = ? WHERE sensor_id = ?"
        values = (data.serial_no, data.sensor_id)
        self.db_connector.execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM sensors WHERE sensor_id = ?"
        values = (data,)
        self.db_connector.execute(query, values)

class DBAdapterMoisture(DBAdapter):
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def select(self, target: plant):
        query = "SELECT * FROM moisture WHERE plant = ?"
        values = (target.plant_id,)
        return self.db_connector.execute(query, values)

    def insert(self, data: moisture):
        query = "INSERT INTO moisture (plant, value, timestamp) VALUES (?, ?, ?)"
        values = (data.plant, data.value, data.timestamp)
        self.db_connector.execute(query, values)

    def update(self, data: moisture):
        query = "UPDATE moisture SET plant = ?, value = ?, timestamp = ? WHERE moisture_id = ?"
        values = (data.plant, data.value, data.timestamp, data.moisture_id)
        self.db_connector.execute(query, values)

    def delete(self, data: moisture):
        query = "DELETE FROM moisture WHERE moisture_id = ?"
        values = (data.moisture_id,)
        self.db_connector.execute(query, values)
