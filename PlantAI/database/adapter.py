"""
Description:
    Database adapter for each table, supports select, insert, update and delete statements
Author: Tim Grundey
Created: 25.09.2025
"""

from abc import ABC, abstractmethod
from database.connector import execute, fetchall, fetchone
from core.models import plant, channel, species, measurement

class DBAdapter(ABC):
    @abstractmethod
    def getList(self) -> list:
        """
        Returns a list with all entries.
        
        :return: List with all entries.
        :rtype: list[plant, species, measurement]
        """
        pass

    @abstractmethod
    def exists(self) -> int:
        """
        Checks if any entries exist in the database table.
        
        :return: Returns true if entries exist.
        :rtype: bool
        """
        pass

    @abstractmethod
    def existsId(self, id: int) -> int:
        """
        Checks if an entry with a matching ID exist in the database table.
        
        :param id: Entry to check for.
        :type id: int

        :return: Returns true if a matching entry exist.
        :rtype: bool
        """
        pass

    @abstractmethod
    def insert(self, data):
        """
        Inserts a new database entry.
        
        :param data: New entry.
        :type data: plant, species, measurement
        """
        pass

    @abstractmethod
    def update(self, data):
        """
        Updates the selected database entry with new values.
        
        :param data: Entry with updated values.
        :type data: plant, species, measurement
        """
        pass

    @abstractmethod
    def delete(self, data: int):
        """
        Deletes the selected database entry.
        
        :param data: Entry to delete.
        :type data: int
        """
        pass

class DBAdapterPlant(DBAdapter):
    def getList(self) -> list[plant]:
        query = "SELECT * FROM plants"
        allPlants = []

        # Create a list of plants
        for entry in fetchall(query):
            allPlants.append(plant(plantId=entry[0], speciesId=entry[1], name=entry[2], location=entry[3]))
        return allPlants
    
    def getChannel(self, mode: str = "all") -> list[channel]:
        """
        Returns a list of input channels with their assigned plants.

        :param mode:
            Sets the mode which channels are returned: \n
            - [assigned]: Returns only channels which have a plant assigned.
            - [all]: Returns all channels.
        :type mode: str

        :return: List with input channels.
        :rtype: list[channel]
        """

        where = ""
        if mode == "assigned":
            # Override WHERE for returning assigned channels
            where = "WHERE p.plantId IS NOT NULL"

        query = f"""
            SELECT c.channelId, c.chMoisture, c.chTemperature, c.desc, c.plantId, p.name FROM channel AS c
            LEFT JOIN plants AS p ON c.plantId = p.plantId
            {where}
            """
        
        allChannels = []
        for entry in fetchall(query):
            allChannels.append(channel(channelId=entry[0], chMoisture=entry[1], chTemperature=entry[2], 
                                       chDescription=entry[3], plantId=entry[4], plantName=entry[5]))
        return allChannels
    
    def exists(self) -> int:
        query = "SELECT EXISTS (SELECT 1 FROM plants)"
        return fetchone(query,)

    def existsId(self, id: int) -> int:
        query = "SELECT EXISTS (SELECT 1 FROM plants WHERE plantId = ?)"
        values = (id,)
        return fetchone(query, values)

    def insert(self, data: plant):
        query = "INSERT INTO plants (speciesId, name, location) VALUES (?, ?, ?)"
        values = (data.speciesId, data.name, data.location)
        execute(query, values)

    def update(self, data: plant):
        query = "UPDATE plants SET speciesId = ?, name = ?, location = ? WHERE plantId = ?"
        values = (data.speciesId, data.name, data.location, data.plantId)
        execute(query, values)

    def updateChannel(self, plantId: int, channelId: int):
        """
        Assign a plant to an input channel.
        
        :param plantId: Plant to be assigned.
        :type plantId: int
        :param channelId: Input channel the plant is assigned to.
        :type channelId: int
        """
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
    
    def existsId(self, id: int) -> int:
        query = "SELECT EXISTS (SELECT 1 FROM species WHERE speciesId = ?)"
        values = (id,)
        return fetchone(query, values)

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

        :param plant: Plant the measurement belongs to.
        :type plant: int
        :param mode:
            Sets the mode which measurement is returned: \n
            - [recent]: Returns the most recent measurement.
            - [old]: The oldest non-archived (minUntilDry = -1) measurement.
        :type mode: str

        :return: Single measurement.
        :rtype: measurement
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

        :param plant: Plant the measurements belong to.
        :type plant: int
        :param limit: Limits the amount of measurements returned (-1 = unlimited).
        :type limit: int
        :param mode:
            Sets the mode which measurements are returned: \n
            - [archived]: Only archived measurements.
            - [current]: Only non-archived (minUntilDry = -1) measurements.
            - [all]: All saved measurements.
        :type mode: str

        :return: List with measurements.
        :rtype: list[measurement]
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
    
    def existsId(self, id: int):
        query = "SELECT EXISTS (SELECT 1 FROM measurements WHERE measureId = ?)"
        values = (id,)
        return fetchone(query, values)

    def insert(self, data: measurement):
        query = "INSERT INTO measurements (plantId, moisture, temperature, minUntilDry, timestamp) VALUES (?, ?, ?, ?, ?)"
        values = (data.plantId, data.moisture, data.temperature, data.minUntilDry, data.timestamp)
        execute(query, values)

    def update(self, id: int, min: int):
        query = "UPDATE measurements SET minUntilDry = ? WHERE measureId = ?"
        values = (min, id)
        execute(query, values)

    def delete(self, data: int):
        query = "DELETE FROM measurements WHERE plantId = ?"
        values = (data,)
        execute(query, values)
