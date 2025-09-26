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

    def execute(self, query: str):
        self.connect()
        self.cur.execute(query)
        self.con.commit()

        # Return results if it's a SELECT query
        return self.cur.fetchall()

    def close(self):
        self.con.close()
