import sys
from abc import ABC, abstractmethod
from database.DBAdapter import DBAdapter, DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from data.Models import plant, species, sensor
from weather.OpenMeteo import OpenMeteo

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
            elif "delete" in userInput:
                if "plant" in userInput:
                    self.deleteEntry(self.dbAdapterPlant)
                elif "species" in userInput:
                    self.deleteEntry(self.dbAdapterSpecies)
                elif "sensor" in userInput:
                    self.deleteEntry(self.dbAdapterSensor)
            elif "show" in userInput:
                if "plant" in userInput:
                    self.showEntry(self.dbAdapterPlant)
                elif "species" in userInput:
                    self.showEntry(self.dbAdapterSpecies)
                elif "sensor" in userInput:
                    self.showEntry(self.dbAdapterSensor)
                elif "measurements" in userInput:
                    self.showMeasurements(self.dbAdapterMeasurement)
            elif userInput == "weather":
                self.weather()
            elif userInput == "help":
                self.help()
            elif userInput == "exit" or userInput == "bye":
                self.bye()
            else:
                print("Unknown command. Type 'help' for a list of commands.")

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
            print("Choose I2C-Address:")
            userInputI2C = input(">>> ")

            # Fill data with user input
            data = sensor(i2cAddress=userInputI2C)
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

        # Get all objects from database and print
        result = dbAdapter.getList()
        for object in result:
            print(object.__str__())

    # Show measurements
    def showMeasurements(self, dbAdapter: DBAdapterMeasurement):
        print("Choose a sensor to show (ID):")
        userInputId = input(">>> ")
        print("Choose how many entries:")
        userInputEntries = input(">>> ")

        print("[ID | Sensor (ID) | Moisture | Temperature | Timestamp]")
        print("-------------------------------------------------------")

        # Get all objects from database and print
        result = dbAdapter.getList(where=int(userInputId), limit=int(userInputEntries))
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

    # Show help
    def help(self):
        print("Available commands:")
        print("  add [plant,species,sensor]     Add a new plant, species or sensor")
        print("  delete [plant,species,sensor]  Delete a plant, species or sensor")
        print("  show [plant,species,sensor]    Show all plants, species or sensors")
        print("  weather                        Show weather forecast")
        print("  help                           Show this help message")
        print("  exit,bye                       Exit")

    # Exit
    def bye(self):
        print("Goodbye!")
        sys.exit()
