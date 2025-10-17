"""
Description:
    Initializes the I2C moisture sensors and reads their data periodically
Author: Tim Grundey
Created: 10.10.2025
"""

import busio
import time
import platform
from adafruit_seesaw.seesaw import Seesaw
from datetime import datetime
from config.loader import getConfig
from core.models import sensor, measurement
from database.DBAdapter import DBAdapterMeasurement

class Measurements:
    def __init__(self):
        self.SensorToSeesaw = {sensor : Seesaw}

    def initSensor(self, allSensors : list[sensor]):
        # Skip initialization if not running on Jetson Nano
        if "tegra" in platform.release():
            from board import SCL, SDA
            i2c = busio.I2C(SCL, SDA)

            # Create dictionary to connect each sensor with its seesaw object
            for sen in allSensors:
                self.SensorToSeesaw = {sen : Seesaw(i2c, addr=sen.i2cAddress)}
        else:
            print(f"Sensor initialization skipped! (not running on Jetson Nano)")
    
    def read(self, dbAdapter: DBAdapterMeasurement):
        while True:
            # Skip reading sensor data if not running on Jetson Nano
            if "tegra" in platform.release():
                # Read moisture and temperature, insert it into database
                for sen, see in self.SensorToSeesaw.items():
                    dbAdapter.insert(measurement(sen.sensorId, see.moisture_read(), see.get_temp(), datetime.now()))
            else:
                # Insert dummy values
                dbAdapter.insert(measurement(1, 400, 23.0, datetime.now()))
            # Wait until next reading
            sleep = getConfig("core", "readIntervalSensors")
            time.sleep(sleep)
