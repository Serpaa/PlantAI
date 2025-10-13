"""
Description: 
    Main class of PlantAI
Author: Tim Grundey
Created: 24.09.2025
"""

import os
import threading
from core.measurements import Measurements
from database.DBConnector import SQLiteDB
from database.DBAdapter import DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from interface.hmi import hmiConsole

# Initialize database connection
dbURL = "PlantAI/database/PlantAI.db"
db = SQLiteDB(dbURL)

# Create database if it doesn't exist
if not os.path.exists(dbURL):
    db.create()

# Initialize database adapters
dbAdapterPlant = DBAdapterPlant(db)
dbAdapterSpecies = DBAdapterSpecies(db)
dbAdapterSensor = DBAdapterSensor(db)
dbAdapterMeasurement = DBAdapterMeasurement(db)

# Initialize each sensor
measurements = Measurements()
measurements.initSensor(dbAdapterSensor.getList())

# Start new thread for reading sensor data
thread = threading.Thread(target=measurements.read, args=(dbAdapterMeasurement,), daemon=True)
thread.start()

# Initialize Console
hmi = hmiConsole(dbAdapterPlant, dbAdapterSpecies, dbAdapterSensor, dbAdapterMeasurement)
hmi.selection()
