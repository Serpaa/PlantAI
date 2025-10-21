"""
Description:
    Interface for basic database and show commands using the CLI
Author: Tim Grundey
Created: 30.09.2025
"""

import sys
from abc import ABC, abstractmethod
from database.DBAdapter import DBAdapter, DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from database.Export import createCSV
from core.models import plant, species, sensor
from api.OpenMeteo import OpenMeteo

class hmi(ABC):
    @abstractmethod
    def addEntry(self):
        pass

    @abstractmethod
    def deleteEntry(self):
        pass

    @abstractmethod
    def help(self):
        pass

    @abstractmethod
    def bye(self):
        pass

class hmiConsole(hmi):
    def __init__(self, dbAdapterPlant: DBAdapterPlant, dbAdapterSpecies: DBAdapterSpecies, dbAdapterSensor: DBAdapterSensor, dbAdapterMeasurement: DBAdapterMeasurement):
        self.dbAdapterPlant = dbAdapterPlant
        self.dbAdapterSpecies = dbAdapterSpecies
        self.dbAdapterSensor = dbAdapterSensor
        self.dbAdapterMeasurement = dbAdapterMeasurement

    def selection(self):
        print("Welcome to PlantAI!")
        while True:
            # Wait for user input
            userInput = input(">>> ")

            # Choose action based on input
            if "add" in userInput:
                if "plant" in userInput:
                    self.addEntry(self.dbAdapterPlant)
                elif "species" in userInput:
                    self.addEntry(self.dbAdapterSpecies)
                elif "sensor" in userInput:
                    self.addEntry(self.dbAdapterSensor)
                else:
                    self.unknown()
            elif "delete" in userInput:
                if "plant" in userInput:
                    self.deleteEntry(self.dbAdapterPlant)
                elif "species" in userInput:
                    self.deleteEntry(self.dbAdapterSpecies)
                elif "sensor" in userInput:
                    self.deleteEntry(self.dbAdapterSensor)
                elif "measure" in userInput:
                    self.deleteEntry(self.dbAdapterMeasurement)
                else:
                    self.unknown()
            elif "show" in userInput:
                if "plant" in userInput:
                    self.showEntry(self.dbAdapterPlant)
                elif "species" in userInput:
                    self.showEntry(self.dbAdapterSpecies)
                elif "sensor" in userInput:
                    self.showEntry(self.dbAdapterSensor)
                elif "measure" in userInput:
                    self.showEntry(self.dbAdapterMeasurement)
                else:
                    self.unknown()
            elif userInput == "weather":
                self.weather()
            elif userInput == "export":
                self.exportEntry(self.dbAdapterMeasurement)
            elif userInput == "help":
                self.help()
            elif userInput == "exit" or userInput == "bye":
                self.bye()
            else:
                self.unknown()

    # Add new entry
    def addEntry(self, dbAdapter: DBAdapter):
        if isinstance(dbAdapter, DBAdapterPlant):
            print("Choose a name:")
            userInputName = input(">>> ")
            print("Choose a species (ID):")
            userInputSpecies = input(">>> ")
            print("Choose a sensor (ID):")
            userInputSensor = input(">>> ")
            print("Plant added!")

            # Fill data with user input
            data = plant(name=userInputName, speciesId=userInputSpecies, sensorId=userInputSensor)

        elif isinstance(dbAdapter, DBAdapterSpecies):
            print("Choose a name:")
            userInputName = input(">>> ")

            # Fill data with user input
            data = species(name=userInputName)
            print("Species added!")

        elif isinstance(dbAdapter, DBAdapterSensor):
            print("Choose I2C-Address (hex: 0x36):")
            userInputI2C = input(">>> ")

            # Fill data with user input
            data = sensor(i2cAddress=int(userInputI2C, 16))
            print("Sensor added!")

        # Add entry to database
        dbAdapter.insert(data)

    # Delete entry
    def deleteEntry(self, dbAdapter: DBAdapter):
        if isinstance(dbAdapter, DBAdapterPlant):
            print("Choose a plant to delete (ID):")
            userInput = input(">>> ")

        elif isinstance(dbAdapter, DBAdapterSpecies):
            print("Choose a species to delete (ID):")
            userInput = input(">>> ")

        elif isinstance(dbAdapter, DBAdapterSensor):
            print("Choose a sensor to delete (ID):")
            userInput = input(">>> ")
        
        elif isinstance(dbAdapter, DBAdapterMeasurement):
            print("Choose a sensor to delete (ID):")
            userInput = input(">>> ")

        # Delete entry from database
        try:
            dbAdapter.delete(userInput)
            print(f"Entry {userInput} deleted!")
        except Exception as ex:
            print(ex)

    # Show entries
    def showEntry(self, dbAdapter: DBAdapter):
        if isinstance(dbAdapter, DBAdapterPlant):
            print("[ID | Species (ID) | Sensor (ID) | Name]")
            print("----------------------------------------")

        elif isinstance(dbAdapter, DBAdapterSpecies):
            print("[ID | Name]")
            print("-----------")

        elif isinstance(dbAdapter, DBAdapterSensor):
            print("[ID | I2C-Address]")
            print("------------------")

        elif isinstance(dbAdapter, DBAdapterMeasurement):
            print("Choose a sensor to show (ID):")
            userInputId = input(">>> ")
            print("Choose how many entries:")
            userInputEntries = input(">>> ")

            print("[ID | Sensor (ID) | Moisture | Temperature | Timestamp]")
            print("-------------------------------------------------------")

        # Get all objects from database
        if isinstance(dbAdapter, DBAdapterPlant) or isinstance(dbAdapter, DBAdapterSpecies) or isinstance(dbAdapter, DBAdapterSensor):
            result = dbAdapter.getList()
        elif isinstance(dbAdapter, DBAdapterMeasurement):
            result = dbAdapter.getList(where=int(userInputId), limit=int(userInputEntries))

        # Print all objects
        for object in result:
            print(object.__str__())

    # Show weather
    def weather(self):
        print("Choose a location:")
        userInput = input(">>> ")

        try:
            # Get weather for location
            print(OpenMeteo().getWeather(userInput))
        except Exception as ex:
            print(ex)

    # Export entry
    def exportEntry(self, dbAdapter: DBAdapter):
        print("Choose a sensor to export (ID):")
        userInputId = input(">>> ")
        
        # Get all objects from database (-1 = unlimited)
        result = dbAdapter.getList(where=int(userInputId), limit=int(-1))

        # Create export
        createCSV(result)
        print("Export created!")

    # Show help
    def help(self):
        print("Available commands:")
        print("  add [plant,species,sensor]             Add a new plant, species or sensor")
        print("  delete [plant,species,sensor,measure]  Delete a plant, species, sensor or measurement")
        print("  show [plant,species,sensor,measure]    Show all plants, species, sensors or measurements")
        print("  weather                                Show weather forecast")
        print("  export                                 Exports all measurements to CSV")
        print("  help                                   Show this help message")
        print("  exit,bye                               Exit")
    
    # Unknown command
    def unknown(self):
        print("Unknown command. Type 'help' for a list of commands.")

    # Exit
    def bye(self):
        print("Goodbye!")
        sys.exit()
