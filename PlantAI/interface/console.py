"""
Description:
    Interface for basic database and show commands using the CLI
Author: Tim Grundey
Created: 30.09.2025
"""

import sys
from database.adapter import DBAdapter, DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from database.export import createCSV
from core.models import plant, species, sensor
from api.OpenMeteo import getWeather

def mainMenu(dbAdapterPlant: DBAdapterPlant, dbAdapterSpecies: DBAdapterSpecies, dbAdapterSensor: DBAdapterSensor, dbAdapterMeasurement: DBAdapterMeasurement):
    print("Welcome to PlantAI!")
    while True:
        # Wait for user input
        userInput = input(">>> ")

        # Choose action based on input
        if "add" in userInput:
            if "plant" in userInput:
                addEntry(dbAdapterPlant)
            elif "species" in userInput:
                addEntry(dbAdapterSpecies)
            elif "sensor" in userInput:
                addEntry(dbAdapterSensor)
            else:
                unknown()
        elif "delete" in userInput:
            if "plant" in userInput:
                deleteEntry(dbAdapterPlant)
            elif "species" in userInput:
                deleteEntry(dbAdapterSpecies)
            elif "sensor" in userInput:
                deleteEntry(dbAdapterSensor)
            elif "measure" in userInput:
                deleteEntry(dbAdapterMeasurement)
            else:
                unknown()
        elif "show" in userInput:
            if "plant" in userInput:
                showEntry(dbAdapterPlant)
            elif "species" in userInput:
                showEntry(dbAdapterSpecies)
            elif "sensor" in userInput:
                showEntry(dbAdapterSensor)
            elif "measure" in userInput:
                showEntry(dbAdapterMeasurement)
            else:
                unknown()
        elif userInput == "weather":
            weather()
        elif userInput == "export":
            exportEntry(dbAdapterMeasurement)
        elif userInput == "help":
            help()
        elif userInput == "exit" or userInput == "bye":
            bye()
        else:
            unknown()

# Add new entry
def addEntry(dbAdapter: DBAdapter):
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

        print("Choose a min. Moisture:")
        userInputMoisture = input(">>> ")

        # Fill data with user input
        data = species(name=userInputName, minMoisture=userInputMoisture)
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
def deleteEntry(dbAdapter: DBAdapter):
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
def showEntry(dbAdapter: DBAdapter):
    if isinstance(dbAdapter, DBAdapterPlant):
        print("[ID | Species (ID) | Sensor (ID) | Name]")
        print("----------------------------------------")

    elif isinstance(dbAdapter, DBAdapterSpecies):
        print("[ID | Name | min. Moisture]")
        print("---------------------------")

    elif isinstance(dbAdapter, DBAdapterSensor):
        print("[ID | I2C-Address]")
        print("------------------")

    elif isinstance(dbAdapter, DBAdapterMeasurement):
        print("Choose a sensor to show (ID):")
        userInputId = input(">>> ")
        print("Choose how many entries:")
        userInputEntries = input(">>> ")

        print("[ID | Sensor (ID) | Moisture | Temperature | Minutes until Dry | Timestamp]")
        print("---------------------------------------------------------------------------")

    # Get all objects from database
    if isinstance(dbAdapter, DBAdapterPlant) or isinstance(dbAdapter, DBAdapterSpecies) or isinstance(dbAdapter, DBAdapterSensor):
        result = dbAdapter.getList()
    elif isinstance(dbAdapter, DBAdapterMeasurement):
        result = dbAdapter.getList(where=int(userInputId), limit=int(userInputEntries))

    # Print all objects
    for object in result:
        print(object.__str__())

# Show weather
def weather():
    print("Choose a location:")
    userInput = input(">>> ")

    try:
        # Get weather for location
        print(getWeather(userInput))
    except Exception as ex:
        print(ex)

# Export entry
def exportEntry(dbAdapter: DBAdapter):
    print("Choose a sensor to export (ID):")
    userInputId = input(">>> ")
    
    # Get all objects from database (-1 = unlimited)
    result = dbAdapter.getList(where=int(userInputId), limit=int(-1))

    # Create export
    createCSV(result)
    print("Export created!")

# Show help
def help():
    print("Available commands:")
    print("  add [plant,species,sensor]             Add a new plant, species or sensor")
    print("  delete [plant,species,sensor,measure]  Delete a plant, species, sensor or measurement")
    print("  show [plant,species,sensor,measure]    Show all plants, species, sensors or measurements")
    print("  weather                                Show weather forecast")
    print("  export                                 Exports all measurements to CSV")
    print("  help                                   Show this help message")
    print("  exit,bye                               Exit")

# Unknown command
def unknown():
    print("Unknown command. Type 'help' for a list of commands.")

# Exit
def bye():
    print("Goodbye!")
    sys.exit() 
