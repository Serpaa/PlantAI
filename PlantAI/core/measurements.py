"""
Description:
    Initialize ADS1115 A/D-Converter and read moisture and temperature from truebner SMT50
Author: Tim Grundey
Created: 10.10.2025
"""

import logging
import time
import platform
from datetime import datetime
from core.models import measurement
from core.predictions import trainModel
from database.adapter import DBAdapterMeasurement
from system.loader import getConfig

# Constants
format = "%Y/%m/%d %H:%M" # Timestamp format

if "tegra" in platform.release():    
    # Initialize ADS1115 via I2C
    import ADS1x15
    ads = ADS1x15.ADS1115(7, 0x48)

    # Set the max. Voltage to be measured
    ads.setGain(ads.PGA_4_096V)
else:
    print(f"Sensor initialization skipped! (not running on Jetson Nano)")

def readVoltage(channel : int) -> float:
    """Returns the current voltage [V] of channel 0..3."""
    # Scale raw input to voltage (0..3V)
    return ads.toVoltage(ads.readADC(channel))

def readMoisture(cycle : int) -> float:
    """Returns the current average volumetric water content [%]."""
    # Scale voltage (0..3V) to volumetric water content (0..50%)
    totalMoisture = 0.0
    for x in range(cycle): # Return average value
        moisture = (readVoltage(0) * 50.0) / 3.0
        totalMoisture += moisture
        time.sleep(1)
    return round(totalMoisture / cycle, 2) # auf 2 Nachkommastellen runden

def readTemperature(cycle : int) -> float:
    """Returns the current average temperature [°C]."""
    # Scale voltage (0..3V) to temperature (-20..85°C)
    totalTemperature = 0.0
    for x in range(cycle): # Return average value
        temperature = (readVoltage(1) - 0.5) * 100.0
        totalTemperature += temperature
        time.sleep(1)
    return round(totalTemperature / cycle, 2) # auf 2 Nachkommastellen runden

def watered(old : float, new : float) -> bool:
    """Returns true if moisture increased significantly between old and new measurement."""
    threshold = getConfig("core", "measurements", "wateredThreshold")
    if new - old > threshold:
        return True
    else:
        return False

def saveMeasurement(dbAdapter: DBAdapterMeasurement):
    """Saves the current moisture and temperature measurements every x minutes."""
    # Skip reading sensor data if not running on Jetson Nano
    if "tegra" in platform.release():
        while True:
            # Check if reading mode is interval or debug
            mode = getConfig("core", "measurements", "readMode")
            if mode == "interval":
                # Wait until reading
                sleep = getConfig("core", "measurements", "readIntervalSensors")
                time.sleep(sleep)

                # Check if recent measurement exists
                skipInsert = False
                recentMeasurement = dbAdapter.getSingle(sensor=1, mode="recent")
                if recentMeasurement is None:
                    logging.info("No recent measurement found. Watering check skipped.")
                # Check if plant got watered since last measurement
                elif watered(recentMeasurement.moisture, readMoisture(1)):
                    # Set minutes until dry for all previous measurements
                    logging.info("Watering detected.")
                    setMinutesUntilDry(dbAdapter, recentMeasurement)

                    # Train model using the now archived measurements
                    trainModel(dbAdapter)
                    skipInsert = True

                # Skip insert after minutes until dry were set
                if not skipInsert:
                    # Format timestamp
                    now = datetime.now()
                    timestamp = now.strftime(format)

                    # Read moisture and temperature from SMT50 (-1 = non-archived entry)
                    dbAdapter.insert(measurement(1, readMoisture(5), readTemperature(5), -1, timestamp))
            elif mode == "debug":
                # Print data directly
                print(f"Sensor - Moisture: {readVoltage(0):.2f}V = {readMoisture(1)}%, Temperature: {readVoltage(1):.2f}V = {readTemperature(1)}°C")
                
                # Wait until next reading
                time.sleep(1)

def setMinutesUntilDry(dbAdapter: DBAdapterMeasurement, recentMeasurement : measurement):
    """Set Minutes until Dry for all non-archived measurements."""
    # Format recent timestamp
    recentTime = datetime.strptime(recentMeasurement.timestamp, format)

    for entry in dbAdapter.getList(sensor=1, limit=-1, mode="current"):
        # Format current timestamp
        actTime = datetime.strptime(entry.timestamp, format)

        # Calculate minutes until dry
        sekUntilDry = recentTime - actTime
        minUntilDry = sekUntilDry.total_seconds() / 60.0

        # Update every measurement
        dbAdapter.update(entry.measureId, minUntilDry)
            
    # Logging
    logging.info("Minutes until dry set.")