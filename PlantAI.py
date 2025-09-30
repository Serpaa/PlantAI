import os
from database.DBConnector import SQLiteDB
from database.DBAdapter import DBAdapterPlant, DBAdapterSpecies, DBAdapterSensor
from hmi.hmi import hmiConsole

# Initialize database connection
dbURL = "database/PlantAI.db"
db = SQLiteDB(dbURL)

# Create database if it doesn't exist
if not os.path.exists(dbURL):
    db.create()

# Initialize Console
hmi = hmiConsole(DBAdapterPlant(db), DBAdapterSpecies(db), DBAdapterSensor(db))
