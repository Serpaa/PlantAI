"""
Description:
    Interface for basic database and show commands using the CLI
Author: Tim Grundey
Created: 30.09.2025
"""

import logging, sys
from api.weather import getForecast
from database.adapter import DBAdapter, DBAdapterPlant, DBAdapterSpecies, DBAdapterMeasurement
from core.measurements import readMoisture
from core.models import plant, species
from core.predictions import trainModel, predictTimeUntilDry
from system.streams import exportAsCSV, importFromCSV

def mainMenu(dbAdapterPlant: DBAdapterPlant, dbAdapterSpecies: DBAdapterSpecies, dbAdapterMeasurement: DBAdapterMeasurement):
    """Main Menu of the console interface."""
    print("Welcome to PlantAI!")
    while True:
        # Wait for user input
        userInput = input(">>> ")

        # Choose action based on input
        if "add" in userInput:
            if "plant" in userInput:
                addEntry(dbAdapterPlant, dbAdapterSpecies)
            elif "species" in userInput:
                addEntry(dbAdapterSpecies)
            else:
                unknown()
        elif "delete" in userInput:
            if "plant" in userInput:
                deleteEntry(dbAdapterPlant)
            elif "species" in userInput:
                deleteEntry(dbAdapterSpecies)
            elif "measure" in userInput:
                deleteEntry(dbAdapterMeasurement, dbAdapterPlant)
            else:
                unknown()
        elif "show" in userInput:
            if "plant" in userInput:
                showEntry(dbAdapterPlant)
            elif "species" in userInput:
                showEntry(dbAdapterSpecies)
            elif "measure" in userInput:
                showEntry(dbAdapterMeasurement, dbAdapterPlant)
            else:
                unknown()
        elif "assign" in userInput:
            assignPlant(dbAdapterPlant)
        elif "csv" in userInput:
            if "import" in userInput:
                importEntry(dbAdapterMeasurement, dbAdapterPlant)
            elif "export" in userInput:
                exportEntry(dbAdapterMeasurement, dbAdapterPlant)
            else:
                unknown()
        elif "model" in userInput:
            if "train" in userInput:
                train(dbAdapterMeasurement)
            elif "predict" in userInput:
                predict()
            else:
                unknown()
        elif userInput == "weather":
            weather()
        elif userInput == "help":
            help()
        elif userInput == "exit" or userInput == "bye":
            bye()
        else:
            unknown()

# Add new entry
def addEntry(dbAdapter: DBAdapter, showAdapter: DBAdapter = None):
    """Add a new entry to the database."""
    if isinstance(dbAdapter, DBAdapterPlant):
        print("Choose a name:")
        userInputName = input(">>> ")

        print("Choose a location:")
        print("[0] inside")
        print("[1] outside")

        while True:
            # Loop selection in case the input is invalid
            userInputLocation = input(">>> ")

            try:
                # Convert input to int
                userInputLocation = int(userInputLocation)
            except ValueError:
                print("Please enter a number.")
                continue

            # Select location based on input
            if userInputLocation == 0:
                inputLocation = "inside"
                break
            elif userInputLocation == 1:
                inputLocation = "outside"
                break
            else:
                print("Location not available. Please try again.")

        # Check if any species exist
        print("Choose a species (ID):")
        if showAdapter.exists() == 1:
            showEntryBrief(showAdapter)
            userInputSpecies = input(">>> ")
        else:
            print("No species available to select, please add one first. Returning to menu ...")
            return

        # Fill data with user input
        data = plant(name=userInputName, location=inputLocation, speciesId=userInputSpecies)
        print("Plant added!")

    elif isinstance(dbAdapter, DBAdapterSpecies):
        print("Choose a name:")
        userInputName = input(">>> ")

        print("Choose a min. Moisture:")
        userInputMoisture = input(">>> ")

        # Fill data with user input
        data = species(name=userInputName, minMoisture=userInputMoisture)
        print("Species added!")

    # Add entry to database
    dbAdapter.insert(data)

# Delete entry
def deleteEntry(dbAdapter: DBAdapter, showAdapter: DBAdapter = None):
    """Deletes the selected entry from the database."""
    if isinstance(dbAdapter, DBAdapterPlant):
        # Check if any plants exist
        if dbAdapter.exists() == 1:
            print("Choose a plant to delete (ID):")
            showEntryBrief(dbAdapter)
            userInput = input(">>> ")
        else:
            print("No plants available to delete.")
            return

    elif isinstance(dbAdapter, DBAdapterSpecies):
        # Check if any species exist
        if dbAdapter.exists() == 1:
            print("Choose a species to delete (ID):")
            showEntryBrief(dbAdapter)
            userInput = input(">>> ")
        else:
            print("No species available to delete.")
            return
    
    elif isinstance(dbAdapter, DBAdapterMeasurement):
        # Check if any measurements exist
        if dbAdapter.exists() == 1:
            print("Choose for which plant (ID) to delete the measurements:")
            showEntryBrief(showAdapter)
            userInput = input(">>> ")
        else:
            print("No measurements available to delete.")
            return

    try:
        # Delete entry from database
        dbAdapter.delete(userInput)
        print(f"Entry {userInput} deleted!")
    except ValueError as ex:
        print(ex)

# Show entries
def showEntry(dbAdapter: DBAdapter, showAdapter: DBAdapter = None):
    """Prints all entries from a specific table."""
    if isinstance(dbAdapter, DBAdapterPlant):
        # Check if any plants exist
        if dbAdapter.exists() == 1:
            print("[ID | Species (ID) | Name | Location]")
            print("-------------------------------------")
        else:
            print("No plants available to show, please add one first.")
            return

    elif isinstance(dbAdapter, DBAdapterSpecies):
        # Check if any species exist
        if dbAdapter.exists() == 1:
            print("[ID | Name | min. Moisture]")
            print("---------------------------")
        else:
            print("No species available to show, please add one first.")
            return

    elif isinstance(dbAdapter, DBAdapterMeasurement):
        # Check if any measurements exist
        if dbAdapter.exists() == 1:
            print("Choose for which plant (ID) to show the measurements:")
            showEntryBrief(showAdapter)
            userInputId = input(">>> ")

            print("Choose how many entries:")
            userInputEntries = input(">>> ")

            print("[ID | Sensor (ID) | Moisture | Temperature | Minutes until Dry | Timestamp]")
            print("---------------------------------------------------------------------------")
        else:
            print("No measurements available to show.")
            return

    # Get all objects from database
    if isinstance(dbAdapter, DBAdapterPlant) or isinstance(dbAdapter, DBAdapterSpecies):
        result = dbAdapter.getList()
    elif isinstance(dbAdapter, DBAdapterMeasurement):
        result = dbAdapter.getList(plant=int(userInputId), limit=int(userInputEntries), mode="all")

    # Print all objects
    for object in result:
        print(object.strDetail())

# Show entries (brief)
def showEntryBrief(dbAdapter: DBAdapter):
    """Prints a brief description from a specific table."""
    if isinstance(dbAdapter, DBAdapterPlant) or isinstance(dbAdapter, DBAdapterSpecies):
        result = dbAdapter.getList()

        # Print all objects
        for object in result:
            print(object.strBrief())

# Assign plant to input channel
def assignPlant(dbAdapter: DBAdapterPlant):
    # Check if any plants exist
    print("Choose a plant (ID):")
    if dbAdapter.exists() == 1:
        showEntryBrief(dbAdapter)
        userInputPlant = input(">>> ")
    else:
        print("No plant available to select, please add one first. Returning to menu ...")
        return

    print("Choose an input channel (ID):")
    userInputChannel = input(">>> ")

    # Update input channel
    dbAdapter.updateChannel(userInputPlant, userInputChannel)
    print(f"Plant {userInputPlant} assigned to channel {userInputChannel}!")

# Import entry
def importEntry(dbAdapter: DBAdapterMeasurement, showAdapter: DBAdapter = None):
    """Imports measurements of the selected plant as CSV."""
    # Check if any plants exist
    print("Choose a plant (ID) to import the measurements for:")
    if dbAdapter.exists() == 1:
        showEntryBrief(showAdapter)
        userInputId = input(">>> ")
    else:
        print("No plant available to select, please add one first. Returning to menu ...")
        return

    # Insert new data into database
    path = "PlantAI/resources/measurements.csv"
    try:
        for entry in importFromCSV(path=path, plantId=userInputId):
            dbAdapter.insert(entry)
        print("Import successful!")
    except FileNotFoundError:
        print(f"Import failed! No measurement file found.")
        logging.error(f"Import failed! No such file: {path}")

# Export entry
def exportEntry(dbAdapter: DBAdapterMeasurement, showAdapter: DBAdapter = None):
    """Exports measurements of the selected plant as CSV."""
    print("Choose a plant (ID) to export the measurements for:")
    if dbAdapter.exists() == 1:
        showEntryBrief(showAdapter)
        userInputId = input(">>> ")
    else:
        print("No plant available to select, please add one first. Returning to menu ...")
        return
    
    # Get all objects from database (-1 = unlimited)
    result = dbAdapter.getList(plant=int(userInputId), limit=int(-1), mode="all")

    # Create export
    path = "PlantAI/resources/measurements.csv"
    exportAsCSV(path=path, allMeasurements=result)
    print("Export successful!")

# Train model
def train(dbAdapter : DBAdapterMeasurement):
    trainModel(dbAdapter)

# Predictions
def predict():
    """Predicts in how many minutes the plant has to be watered again."""
    # Get moisture and time until dry
    curMoisture = readMoisture(1)
    days, hours = predictTimeUntilDry(curMoisture)

    # Only print answer if prediction was made
    if days == None and hours == None:
        print("Not enough data collected to predict the moisture.")
    else:
        print(f"Prediction - {curMoisture}%: Water in {days} days and {hours} hours.")

# Show weather
def weather():
    """Prints a weather forecast of the current location."""
    try:
        # Get forecast of current location
        print(getForecast())
    except (ValueError, ConnectionError) as ex:
        print(ex)

# Show help
def help():
    """Prints the help menu."""
    print("Available commands:")
    print("  add [plant,species]                Add a new plant or species")
    print("  delete [plant,species,measure]     Delete a plant, species or measurement")
    print("  show [plant,species,measure]       Show all plants, species or measurements")
    print("  assign [plant]                     Assign a plant to an input channel")
    print("  csv [import,export]                Imports or exports all measurements using CSV")
    print("  model [train,predict]              Manually train the model or predict minUntilDry")
    print("  weather                            Show weather forecast")
    print("  help                               Show this help message")
    print("  exit,bye                           Exit")

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
