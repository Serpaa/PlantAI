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
                try:
                    self.SensorToSeesaw = {sen : Seesaw(i2c, addr=sen.i2cAddress)}
                except (RuntimeError, ValueError) as error:
                    print(f"Error: {error}")
        else:
            print(f"Sensor initialization skipped! (not running on Jetson Nano)")
    
    def read(self, dbAdapter: DBAdapterMeasurement):
        # Skip reading sensor data if not running on Jetson Nano
        if "tegra" in platform.release():
            while True:
                # Check if reading mode is interval or debug
                mode = getConfig("core", "readMode")
                for sen, see in self.SensorToSeesaw.items():
                    if mode == "interval":
                        # Format timestamp
                        now = datetime.now()
                        timestamp = now.strftime("%Y/%m/%d %H:%M")

                        # Read moisture multiple times and get average
                        loops = 10; sumMoisture = 0.0
                        for x in range(loops):
                            sumMoisture += see.moisture_read()
                            time.sleep(1)

                        # Calculate average moisture
                        averageMoisture = sumMoisture / loops

                        # Read moisture and temperature, insert it into database
                        dbAdapter.insert(measurement(sen.sensorId, averageMoisture, see.get_temp(), timestamp))
                    elif mode == "debug":
                        # Print moisture directly
                        print(f"Sensor[{sen.sensorId}]: {see.moisture_read()}")

                # Wait until next reading
                sleep = getConfig("core", "readIntervalSensors")
                time.sleep(sleep)
