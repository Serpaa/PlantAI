"""
Description:
    Set up streams to export and import data from and to the database
Author: Tim Grundey
Created: 21.10.2025
"""

import csv
from core.models import measurement

def exportAsCSV(path: str, allMeasurements: list[measurement]):
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)

        # Write header then all data rows
        writer.writerow(["Minutes until Dry", "Moisture", "Temperature", "Timestamp"])
        for object in allMeasurements:
            writer.writerow([object.minUntilDry, int(object.moisture), object.temperature, object.timestamp])

def importFromCSV(path: str, sensorId: int) -> list[measurement]:
    with open(path, newline="") as file:
        reader = csv.reader(file)
        next(reader) # skip header row

        # Create measurement object for every row
        allMeasurements = []
        for row in reader:
            allMeasurements.append(
                measurement(sensorId = sensorId, minUntilDry = row[0], moisture = row[1], temperature = row[2], timestamp = row[3]))
        return allMeasurements