"""
Description: 
    Main class of PlantAI
Author: Tim Grundey
Created: 24.09.2025
"""

# Create log file before importing any other files
import logging
logging.basicConfig(
    filename='PlantAI/resources/plantai.log', filemode='a', level=logging.INFO,
    format='%(asctime)s: %(levelname)s - %(message)s'
)

import os
import threading
from core.measurements import saveMeasurement
from core.measurements import trainModel
from database.connector import createDB
from database.adapter import DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from interface.audio import vad
from interface.console import mainMenu

# Create database if it doesn't exist
dbPath = "PlantAI/database/PlantAI.db"
if not os.path.exists(dbPath):
    createDB("PlantAI/database/PlantAI.sql")

# Initialize database adapters
dbAdapterPlant = DBAdapterPlant()
dbAdapterSpecies = DBAdapterSpecies()
dbAdapterSensor = DBAdapterSensor()
dbAdapterMeasurement = DBAdapterMeasurement()

# Start new thread for reading sensor data
threadSensor = threading.Thread(target=saveMeasurement, args=(dbAdapterMeasurement,), daemon=True)
threadSensor.start()

# Start new thread for voice detection
threadVAD = threading.Thread(target=vad, daemon=True)
threadVAD.start()

# Train model
trainModel(dbAdapterMeasurement)

# Logs
logging.info("System booted.")

# Initialize Console
mainMenu(dbAdapterPlant, dbAdapterSpecies, dbAdapterSensor, dbAdapterMeasurement)
