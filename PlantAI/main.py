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
from system.loader import getConfig

# Create log file
logging.basicConfig(
    filename='PlantAI/system/plantai.log', filemode='a', level=logging.INFO,
    format='%(asctime)s: %(levelname)s - %(message)s'
)

# Create database if it doesn't exist
dbPath = getConfig("database","path")
if not os.path.exists(dbPath):
    createDB()

# Initialize database adapters
dbAdapterPlant = DBAdapterPlant()
dbAdapterSpecies = DBAdapterSpecies()
dbAdapterSensor = DBAdapterSensor()
dbAdapterMeasurement = DBAdapterMeasurement()

# Start new thread for reading sensor data
thread = threading.Thread(target=saveMeasurement, args=(dbAdapterMeasurement,), daemon=True)
thread.start()

# Logs
logging.info("System booted.")

# Initialize Console
mainMenu(dbAdapterPlant, dbAdapterSpecies, dbAdapterSensor, dbAdapterMeasurement)
