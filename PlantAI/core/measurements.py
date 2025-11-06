"""
Description:
    Initialize ADS1115 A/D-Converter and read moisture and temperature from truebner SMT50
Author: Tim Grundey
Created: 10.10.2025
"""

import time
import platform
from datetime import datetime
from core.models import measurement
from database.adapter import DBAdapterMeasurement
from system.loader import getConfig

if "tegra" in platform.release():    
    # Initialize ADS1115 via I2C
    import ADS1x15
    ads = ADS1x15.ADS1115(7, 0x48)

    # Set the max. Voltage to be measured
    ads.setGain(ads.PGA_4_096V)
else:
    print(f"Sensor initialization skipped! (not running on Jetson Nano)")

def readSensor(dbAdapter: DBAdapterMeasurement):
    # Skip reading sensor data if not running on Jetson Nano
    if "tegra" in platform.release():
        while True:
            # Scale raw inputs to voltage (0..3V)
            vMoisture = ads.toVoltage(ads.readADC(0))
            vTemperature = ads.toVoltage(ads.readADC(1))

            # Scale voltage (0..3V) to moisture (0..50%) and temperature (-20..85°C)
            moisture: float = (vMoisture * 50.0) / 3.0
            temperature: float = (vTemperature - 0.5) * 100.0

            # Check if reading mode is interval or debug
            mode = getConfig("core", "readMode")
            if mode == "interval":
                # Format timestamp
                now = datetime.now()
                timestamp = now.strftime("%Y/%m/%d %H:%M")

                # Read moisture and temperature from SMT50
                dbAdapter.insert(measurement(1, moisture, temperature, timestamp))

                # Wait until next reading
                sleep = getConfig("core", "readIntervalSensors")
                time.sleep(sleep)

            elif mode == "debug":
                # Print data directly
                print(f"Sensor - Moisture: {vMoisture:.2f}V = {moisture:.2f}%, Temperature: {vTemperature:.2f}V = {temperature:.2f}°C")
                
                # Wait until next reading
                time.sleep(1)
