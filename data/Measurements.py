import busio
import time
import threading
import platform
from adafruit_seesaw.seesaw import Seesaw
from datetime import datetime
from model.models import sensor, measurement
from database.DBAdapter import DBAdapterMeasurement

class Measurements:
    def __init__(self, allSensors : list[sensor], dbAdapter: DBAdapterMeasurement):
        self.allSensors = allSensors
        self.dbAdapter = dbAdapter
        self.SensorToSeesaw = {sensor : Seesaw}
        self.initSensor()

        # Start new thread for reading sensor data
        thread = threading.Thread(target=self.read, daemon=True)
        thread.start()

    def initSensor(self):
        # Skip initialization if not running on Jetson Nano
        # if should be edited later to Jetson Nano info
        if not platform.processor() == "arm":
            from board import SCL, SDA
            i2c = busio.I2C(SCL, SDA)

            # Create dictionary to connect each sensor with its seesaw object
            for sen in self.allSensors:
                self.SensorToSeesaw = {sen : Seesaw(i2c, addr=sen.i2cAddress)}
        else:
            print(f"Sensor initialization skipped! (not running on Jetson Nano)")
    
    def read(self):
        while True:
            # Skip reading sensor data if not running on Jetson Nano
            # if should be edited later to Jetson Nano info
            if not platform.processor() == "arm":
                # Read moisture and temperature, insert it into database
                for sen, see in self.SensorToSeesaw.items():
                    self.dbAdapter.insert(measurement(sen.sensorId, see.moisture_read(), see.get_temp(), datetime.now()))
            else:
                # Insert dummy values
                self.dbAdapter.insert(measurement(1, 400, 23.0, datetime.now()))
            # Wait until next reading
            time.sleep(60)
