"""
Description:
    Interface for basic database and show commands using the CLI
Author: Tim Grundey
Created: 30.09.2025
"""

import logging
import sys
from api.OpenMeteo import getWeather
from database.adapter import DBAdapter, DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from database.streams import exportAsCSV, importFromCSV
from core.models import plant, species, sensor
from core.predictions import hoursUntilDry
from system.loader import getConfig

def mainMenu(dbAdapterPlant: DBAdapterPlant, dbAdapterSpecies: DBAdapterSpecies, dbAdapterSensor: DBAdapterSensor, dbAdapterMeasurement: DBAdapterMeasurement):
    """Main Menu of the console interface."""
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
        elif "csv" in userInput:
            if "import" in userInput:
                importEntry(dbAdapterMeasurement)
            elif "export" in userInput:
                exportEntry(dbAdapterMeasurement)
            else:
                unknown()
        elif userInput == "predict":
            predict(dbAdapterMeasurement)
        elif userInput == "weather":
            weather()
        elif userInput == "help":
            help()
        elif userInput == "exit" or userInput == "bye":
            bye()
        else:
            unknown()

# Add new entry
def addEntry(dbAdapter: DBAdapter):
    """Add a new entry to the database."""
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
    """Deletes the selected entry from the database."""
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
    """Prints all entries from a specific table."""
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
        result = dbAdapter.getList(sensor=int(userInputId), limit=int(userInputEntries))

    # Print all objects
    for object in result:
        print(object.__str__())

# Import entry
def importEntry(dbAdapter: DBAdapter):
    """Imports measurements of the selected sensor as CSV."""
    print("Choose a sensor to import (ID):")
    userInputId = input(">>> ")

    # Insert new data into database
    path = getConfig("csv", "import")
    for entry in importFromCSV(path=path, sensorId=userInputId):
        dbAdapter.insert(entry)
    print("Import successful!")

# Export entry
def exportEntry(dbAdapter: DBAdapter):
    """Exports measurements of the selected sensor as CSV."""
    print("Choose a sensor to export (ID):")
    userInputId = input(">>> ")
    
    # Get all objects from database (-1 = unlimited)
    result = dbAdapter.getList(sensor=int(userInputId), limit=int(-1))

    # Create export
    path = getConfig("csv", "export")
    exportAsCSV(path=path, allMeasurements=result)
    print("Export successful!")

# Predictions
def predict(dbAdapter: DBAdapterMeasurement):
    """Predicts in how many hours the plant has to be watered again."""
    hoursUntilDry(dbAdapter.getCompleteList(sensor=1, limit=int(-1)))

# Show weather
def weather():
    """Prints a weather forecast of the selected location."""
    print("Choose a location:")
    userInput = input(">>> ")

    try:
        # Get weather for location
        print(getWeather(userInput))
    except Exception as ex:
        print(ex)

# Show help
def help():
    """Prints the help menu."""
    print("Available commands:")
    print("  add [plant,species,sensor]             Add a new plant, species or sensor")
    print("  delete [plant,species,sensor,measure]  Delete a plant, species, sensor or measurement")
    print("  show [plant,species,sensor,measure]    Show all plants, species, sensors or measurements")
    print("  csv [import,export]                    Imports or exports all measurements using CSV")
    print("  predict                                Predict in how many hours the plant soil is dry")
    print("  weather                                Show weather forecast")
    print("  help                                   Show this help message")
    print("  exit,bye                               Exit")

# Unknown command
def unknown():
    """Prints unknown command."""
    print("Unknown command. Type 'help' for a list of commands.")

# Exit
def bye():
    """Exits the system."""
    print("Goodbye!")
    logging.info("System shutdown.")
    sys.exit() 
