"""
Description: 
    Main class of PlantAI
Author: Tim Grundey
Created: 24.09.2025
"""

import os, logging, threading

# Create archive folder for logs
archivePath = "PlantAI/resources/archive"
if not os.path.exists(archivePath):
    os.mkdir(archivePath)

# Create log file
from system.streams import initLog
initLog("PlantAI/resources", "plantai.log")

# Import all other files
from core.measurements import saveMeasurement, trainModel
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

# Train model
trainModel(dbAdapterMeasurement, "BOOT")

# Logs
logging.info("System booted.")

# Initialize Console
mainMenu(dbAdapterPlant, dbAdapterSpecies, dbAdapterMeasurement)
