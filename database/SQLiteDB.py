import sqlite3

class SQLiteDB:
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

    def close(self):
        self.con.close()
