"""
Description: 
    Main class of PlantAI
Author: Tim Grundey
Created: 24.09.2025
"""

import logging
import os
import threading
from core.measurements import Measurements
from database.connector import SQLiteDB
from database.adapter import DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from interface.console import mainMenu
from system.loader import getConfig

# Initialize database connection
dbURL = getConfig("database","path")
db = SQLiteDB(dbURL)

# Create database if it doesn't exist
if not os.path.exists(dbURL):
    db.create()

# Initialize database adapters
dbAdapterPlant = DBAdapterPlant(db)
dbAdapterSpecies = DBAdapterSpecies(db)
dbAdapterSensor = DBAdapterSensor(db)
dbAdapterMeasurement = DBAdapterMeasurement(db)

# Get all sensors from database
measurements = Measurements()
allSensors = dbAdapterSensor.getList()

if len(allSensors) > 0:
    # Initialize each sensor
    measurements.initSensor(allSensors)

    # Start new thread for reading sensor data
    thread = threading.Thread(target=measurements.read, args=(dbAdapterMeasurement,), daemon=True)
    thread.start()

# Create log file
logging.basicConfig(
    filename='PlantAI/system/plantai.log', filemode='a', level=logging.INFO,
    format='%(asctime)s: %(levelname)s - %(message)s'
)

# Initialize Console
mainMenu(dbAdapterPlant, dbAdapterSpecies, dbAdapterSensor, dbAdapterMeasurement)
