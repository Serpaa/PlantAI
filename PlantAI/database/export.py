"""
Description:
    Exports data from the database to other formats
Author: Tim Grundey
Created: 21.10.2025
"""

import csv
from core.models import measurement

def createCSV(allMeasurements: list[measurement]):
    with open("PlantAI/database/measurements.csv", "w", newline="") as file:
        writer = csv.writer(file)

        # Write header then all data rows
        writer.writerow(["Minutes until Dry", "Moisture", "Temperature", "Timestamp"])
        for object in allMeasurements:
            writer.writerow([object.minUntilDry, int(object.moisture), object.temperature, object.timestamp])
