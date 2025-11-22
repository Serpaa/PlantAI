"""
Description:
    Creates and connects the SQLite3 database
Author: Tim Grundey
Created: 25.09.2025
"""

import logging
import sqlite3

def connect():
    """Connect to the SQLite Database."""
    path = "PlantAI/database/PlantAI.db"
    con = sqlite3.connect(path)
    return con, con.cursor()

def createDB(path: str):
    """Creates a new SQLite Database."""
    # Read SQL file
    file = open(path, "r")
    sqlFile = file.read()
    file.close()

    # Split SQL commands
    sqlCommands = sqlFile.split(";")

    # Execute each command
    con, cur = connect()
    for command in sqlCommands:
        try:
            cur.execute(command)
        except sqlite3.OperationalError as msg:
            print("Command skipped: ", msg)
    cur.close()

    # Logs
    logging.info("New database created.")

def execute(query: str, values: tuple = ()):
    """Executes an SQL query without returning a value."""
    con, cur = connect()
    cur.execute(query, values)
    con.commit()

    # Raise exception if no rows were affected
    if cur.rowcount == 0:
        cur.close()
        raise Exception("No matching entry found.")
    cur.close()

def fetchone(query: str, values: tuple = ()):
    """Executes an SQL query and returns one entry."""
    con, cur = connect()
    cur.execute(query, values)
    
    # Return result
    result = cur.fetchone()
    cur.close()
    return result

def fetchall(query: str, values: tuple = ()):
    """Executes an SQL query and returns a list."""
    con, cur = connect()
    cur.execute(query, values)
    
    # Return result
    result = cur.fetchall()
    cur.close()
    return result
