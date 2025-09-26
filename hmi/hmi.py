import threading
from abc import ABC, abstractmethod
from database.DBAdapter import DBAdapterPlant
from model.models import plant

class hmi(ABC):
    @abstractmethod
    def addPlant(self):
        pass

class hmiConsole(hmi):
    def __init__(self, dbAdapter: DBAdapterPlant):
        self.dbAdapter = dbAdapter

        # Start new thread for selection
        thread = threading.Thread(target=self.selection)
        thread.start()

    def selection(self):
        print("Welcome to PlantAI!")
        while True:
            # Wait for user input
            userInput = input(">>> ")

            # Add new plant
            if userInput == "add plant":
                # Todo add user input
                self.dbAdapter.insert(plant(name="Orchidee", species=1, sensor=1))

            # Delete plant
            # Todo

            # View plants
            if userInput == "view plant":
                print(self.dbAdapter.select())

            # Help information
            if userInput == "help":
                print("Available commands:")
                print("  help       Show this help message")
                print("  exit,bye   Exit")

            # Exit
            if userInput == "exit" or userInput == "bye":
                print("Goodbye!")
                break

    def addPlant(self):
        print("Plant added!")
