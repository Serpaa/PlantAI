"""
Description: 
    Main class of PlantAI
Author: Tim Grundey
Created: 24.09.2025
"""

import logging
import os
import threading
from core.measurements import saveMeasurement
from database.connector import createDB
from database.adapter import DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from interface.console import mainMenu
from interface.vad import detect

# Create log file
logging.basicConfig(
    filename='PlantAI/resources/plantai.log', filemode='a', level=logging.INFO,
    format='%(asctime)s: %(levelname)s - %(message)s'
)

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
threadVAD = threading.Thread(target=detect, daemon=True)
threadVAD.start()

# Logs
logging.info("System booted.")

# Initialize Console
mainMenu(dbAdapterPlant, dbAdapterSpecies, dbAdapterSensor, dbAdapterMeasurement)
