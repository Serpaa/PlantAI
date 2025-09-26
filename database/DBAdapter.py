from abc import ABC, abstractmethod
from database.DBConnector import DBConnector

class DBAdapter(ABC):
    @abstractmethod
    def select(self):
        pass

    @abstractmethod
    def insert(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

class DBAdapterPlant(DBAdapter):
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def select(self):
        print(self.db_connector.execute("SELECT * FROM plants"))

    def insert(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass
