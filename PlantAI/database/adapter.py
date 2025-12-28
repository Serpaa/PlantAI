"""
Description:
    Database adapter for each table, supports select, insert, update and delete statements
Author: Tim Grundey
Created: 25.09.2025
"""

from abc import ABC, abstractmethod
from database.connector import execute, fetchall, fetchone
from core.models import plant, species, measurement

class DBAdapter(ABC):
    @abstractmethod
    def getList(self):
        pass

    @abstractmethod
    def exists(self):
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
    def getList(self) -> list[plant]:
        query = "SELECT * FROM plants"
        allPlants = []

        # Create a list of plants
        for entry in fetchall(query):
            allPlants.append(plant(plantId=entry[0], speciesId=entry[1], name=entry[2], location=entry[3]))
        return allPlants
    
    def exists(self) -> int:
        query = "SELECT EXISTS (SELECT 1 FROM plants)"
        return fetchone(query,)

    def insert(self, data: plant):
        query = "INSERT INTO plants (speciesId, name, location) VALUES (?, ?, ?)"
        values = (data.speciesId, data.name, data.location)
        execute(query, values)

    def update(self, data: plant):
        query = "UPDATE plants SET speciesId = ?, name = ?, location = ? WHERE plantId = ?"
        values = (data.speciesId, data.name, data.location, data.plantId)
        execute(query, values)

    def updateChannel(self, plantId: int, channelId: int):
        query = "UPDATE channel SET plantId = ? WHERE channelId = ?"
        values = (plantId, channelId)
        execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM plants WHERE plantId = ?"
        values = (data,)
        execute(query, values)

class DBAdapterSpecies(DBAdapter):
    def getList(self) -> list[species]:
        query = "SELECT * FROM species"    
        allSpecies = []

        # Create a list of species
        for entry in fetchall(query):
            allSpecies.append(species(speciesId=entry[0], name=entry[1], minMoisture=entry[2]))
        return allSpecies
    
    def exists(self) -> int:
        query = "SELECT EXISTS (SELECT 1 FROM species)"
        return fetchone(query,)

    def insert(self, data: species):
        query = "INSERT INTO species (name, minMoisture) VALUES (?, ?)"
        values = (data.name, data.minMoisture)
        execute(query, values)

    def update(self, data: species):
        query = "UPDATE species SET name = ?, minMoisture = ? WHERE speciesId = ?"
        values = (data.name, data.minMoisture, data.speciesId)
        execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM species WHERE speciesId = ?"
        values = (data,)
        execute(query, values)

class DBAdapterMeasurement(DBAdapter):
    def getSingle(self, plant: int, mode: str = "recent") -> measurement:
        """
        Returns a single measurement.

        mode:
            - "recent": The most recent measurement.
            - "old": The oldest non-archived (minUntilDry = -1) measurement.
        """

        # Select ORDER BY direction
        if mode == "recent":
            direction = "DESC"
        elif mode == "old":
            direction = "ASC"

        # Create query
        query = f"""
            SELECT * FROM measurements WHERE plantId = ? AND minUntilDry = '-1'
            ORDER BY timestamp {direction}
            """
        values = (plant,)
        
        # Convert result to measurement
        result = fetchone(query, values)
        if result is None:
            return None
        else:
            return measurement(measureId=result[0],plantId=result[1], moisture=result[2], 
                               temperature=result[3], minUntilDry=result[4], timestamp=result[5])

    def getList(self, plant: int, limit: int, mode: str = "all") -> list[measurement]:
        """
        Returns a list with measurements sorted from old to new.

        mode:
            - "archived": Only archived measurements.
            - "current": Only non-archived (minUntilDry = -1) measurements.
            - "all": All saved measurements.
        """

        # Select WHERE clause
        if mode == "archived":
            whereClause = "AND minUntilDry != '-1'"
        elif mode == "current":
            whereClause = "AND minUntilDry = '-1'"
        elif mode == "all":
            whereClause = ""

        # Create query
        query = f"""
            SELECT * FROM (
                SELECT * FROM measurements WHERE plantId = ? {whereClause}
                ORDER BY timestamp DESC 
                LIMIT ?) 
            ORDER BY timestamp
            """
        values = (plant, limit)
        allMeasurements = []

        # Create a list of measurements
        for result in fetchall(query, values):
            allMeasurements.append(
                measurement(measureId=result[0],plantId=result[1], moisture=result[2], 
                            temperature=result[3], minUntilDry=result[4], timestamp=result[5]))
        return allMeasurements
    
    def exists(self) -> int:
        query = "SELECT EXISTS (SELECT 1 FROM measurements)"
        return fetchone(query,)

    def insert(self, data: measurement):
        """Inserts a new measurement."""
        query = "INSERT INTO measurements (plantId, moisture, temperature, minUntilDry, timestamp) VALUES (?, ?, ?, ?, ?)"
        values = (data.plantId, data.moisture, data.temperature, data.minUntilDry, data.timestamp)
        execute(query, values)

    def update(self, id: int, min: int):
        """Updates minUntilDry for the chosen measureId."""
        query = "UPDATE measurements SET minUntilDry = ? WHERE measureId = ?"
        values = (min, id)
        execute(query, values)

    def delete(self, data: int):
        """Deletes all measurements for the chosen plantId."""
        query = "DELETE FROM measurements WHERE plantId = ?"
        values = (data,)
        execute(query, values)
