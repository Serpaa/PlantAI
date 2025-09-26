import os
from database.DBConnector import SQLiteDB
from database.DBAdapter import DBAdapterPlant
from model.models import plant, species, sensor, moisture

# Initialize database connection
dbURL = "database/PlantAI.db"
db = SQLiteDB(dbURL)

# Create database if it doesn't exist
if not os.path.exists(dbURL):
    db.create()
