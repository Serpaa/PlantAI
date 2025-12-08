"""
Description:
    Set up streams to export and import data from and to the database
Author: Tim Grundey
Created: 21.10.2025
"""

import csv, yaml
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from core.models import measurement

def exportAsCSV(path: str, allMeasurements: list[measurement]):
    """
    Exports a list of measurements as CSV.
    
    :param path: Filepath the CSV is exported to.
    :type path: str
    :param allMeasurements: List of the measurements to be exported.
    :type allMeasurements: list[measurement]
    """
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)

        # Write header then all data rows
        writer.writerow(["Minutes until Dry", "Moisture", "Temperature", "Timestamp"])
        for object in allMeasurements:
            writer.writerow([object.minUntilDry, object.moisture, object.temperature, object.timestamp])
    # Logs
    logging.info("CSV export created.")

def importFromCSV(path: str, sensorId: int) -> list[measurement]:
    """
    Returns a list of measurements from CSV.
    
    :param path: Filepath the CSV is imported from.
    :type path: str
    :param sensorId: Sensor ID the measurements belong to.
    :type sensorId: int

    :return: List of the imported measurements.
    :rtype: list[measurement]
    """
    with open(path, newline="") as file:
        reader = csv.reader(file)
        next(reader) # skip header row

        # Create measurement object for every row
        allMeasurements = []
        for row in reader:
            allMeasurements.append(
                measurement(sensorId = sensorId, minUntilDry = row[0], moisture = row[1], temperature = row[2], timestamp = row[3]))
        return allMeasurements
    # Logs
    logging.info("Imported measurements from CSV.")

def importConfigFromYAML():
    """
    Returns the config stream from YAML.
    
    :return: Stream of the config.
    :rtype: stream
    """
    with open("PlantAI/resources/config.yaml") as stream:
        return yaml.safe_load(stream)

def initLog(path: str, name: str):
    """
    Initializes a rotating log file.

    :param path: Filepath where the log is saved.
    :type path: str
    :param name: Filename of the log file.
    :type name: str
    """
    # Set up rotation
    handler = TimedRotatingFileHandler(
        filename=path + "/" + name, # build filepath
        when="W6", # W0=Monday .. W6=Sunday
        interval=2, # new log file every 2nd Sunday (two weeks)
        backupCount=0 # keep all files
    )

    # Custom function for renaming the rollover file
    # from plantai.log.2025-12-08 to plantai_2025-12-08.log
    def renameLog(default_name):
        # Get default timestamp
        timestamp = default_name.split(".")[-1]

        # Rename and store in archive folder
        strippedName = name.strip(".log") # strip .log from full path
        return f"{path}/archive/{strippedName}_{timestamp}.log"

    # Pass custom rename function to handler
    handler.namer = renameLog

    # Initialize stream
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        format='%(asctime)s: %(levelname)s - %(message)s'
    )
