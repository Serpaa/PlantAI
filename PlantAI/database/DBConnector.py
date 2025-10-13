"""
Description:
    Creates and connects the SQLite3 database
Author: Tim Grundey
Created: 25.09.2025
"""

from abc import ABC, abstractmethod
import sqlite3

class DBConnector(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def execute(self, query: str):
        pass

    @abstractmethod
    def close(self):
        pass

class SQLiteDB(DBConnector):
    def __init__(self, db_path: str):
        self.db_path = db_path
        con = None
        cur = None

    def connect(self):
        self.con = sqlite3.connect(self.db_path)
        self.cur = self.con.cursor()

    def create(self):
        self.connect()

        # Read SQL file
        file = open("database/PlantAI.sql", "r")
        sqlFile = file.read()
        file.close()

        # Split SQL commands
        sqlCommands = sqlFile.split(";")

        # Execute each command
        for command in sqlCommands:
            try:
                self.cur.execute(command)
            except sqlite3.OperationalError as msg:
                print("Command skipped: ", msg)

    def execute(self, query: str, values: tuple = ()):
        self.connect()
        self.cur.execute(query, values)
        self.con.commit()

        if "DELETE" or "UPDATE" in query:
            # Raise exception if no rows were affected during a DELETE query
            if self.cur.rowcount == 0:
                raise Exception("No matching entry found.")
        
        # Return results for SELECT query
        return self.cur.fetchall()

    def close(self):
        self.con.close()
