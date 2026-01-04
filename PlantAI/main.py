"""
Description: 
    Main class of PlantAI
Author: Tim Grundey
Created: 24.09.2025
"""

import os, logging, threading

# Create archive and model folders
folders = ["PlantAI/resources/archive", "PlantAI/resources/models"]
for paths in folders:
    if not os.path.exists(paths):
        os.mkdir(paths)

# Create log file
from system.streams import initLog
initLog("PlantAI/resources", "plantai.log")

# Import all other files
from core.measurements import saveMeasurement
from core.predictions import trainModel
from database.connector import createDB
from database.adapter import DBAdapterPlant, DBAdapterSpecies, DBAdapterMeasurement
from interface.audio import vad
from interface.console import mainMenu

# Create database if it doesn't exist
dbPath = "PlantAI/database/PlantAI.db"
if not os.path.exists(dbPath):
    createDB("PlantAI/database/sql/create.sql")

# Initialize database adapters
dbAdapterPlant = DBAdapterPlant()
dbAdapterSpecies = DBAdapterSpecies()
dbAdapterMeasurement = DBAdapterMeasurement()

# Start new thread for reading sensor data
threadSensor = threading.Thread(target=saveMeasurement, args=(dbAdapterMeasurement,dbAdapterPlant), daemon=True)
threadSensor.start()

# Start new thread for voice detection
threadVAD = threading.Thread(target=vad, daemon=True)
threadVAD.start()

# Logs
logging.info("System booted.")

# Initialize Console
mainMenu(dbAdapterPlant, dbAdapterSpecies, dbAdapterMeasurement)
