import os
from data.Measurements import Measurements
from database.DBConnector import SQLiteDB
from database.DBAdapter import DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor, DBAdapterMeasurement
from hmi.hmi import hmiConsole

# Initialize database connection
dbURL = "database/PlantAI.db"
db = SQLiteDB(dbURL)

# Create database if it doesn't exist
if not os.path.exists(dbURL):
    db.create()

# Initialize database adapters
dbAdapterPlant = DBAdapterPlant(db)
dbAdapterSpecies = DBAdapterSpecies(db)
dbAdapterSensor = DBAdapterSensor(db)
dbAdapterMeasurement = DBAdapterMeasurement(db)

# Initialize each sensor and read moisture and temperature
allSensors = dbAdapterSensor.getList()
measurements = Measurements(allSensors, dbAdapterMeasurement)

# Initialize Console
hmi = hmiConsole(dbAdapterPlant, dbAdapterSpecies, dbAdapterSensor, dbAdapterMeasurement)
hmi.selection()
