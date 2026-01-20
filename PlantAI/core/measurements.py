"""
Description:
    Initialize ADS1115 A/D-Converter and read moisture and temperature from truebner SMT50
Author: Tim Grundey
Created: 10.10.2025
"""

import logging, time, platform, threading
from datetime import datetime
from core.models import measurement
from core.predictions import trainModel
from database.adapter import DBAdapterPlant, DBAdapterMeasurement
from system.streams import importConfigFromYAML

# Configuration
stream = importConfigFromYAML()
config = stream["core"]["measurements"]

# Constants
FORMAT = "%Y/%m/%d %H:%M" # Timestamp format
THRESHOLD = config["wateredThreshold"]
MODE = config["readMode"]
SLEEP = config["readIntervalSensors"]

if "tegra" in platform.release():    
    # Initialize ADS1115 via I2C
    import ADS1x15
    ads = ADS1x15.ADS1115(7, 0x48)

    # Set the max. Voltage to be measured
    ads.setGain(ads.PGA_4_096V)
else:
    logging.warning("Sensor initialization skipped! (not running on Jetson Nano)")

def readVoltage(channel: int) -> float:
    """
    Returns the current voltage [V] of a channel.
    
    :param channel: Channel to be used.
    :type channel: int

    :return: Current voltage in V.
    :rtype: float
    """
    # Scale raw input to voltage (0..3V)
    return ads.toVoltage(ads.readADC(channel))

def readMoisture(channel: int, cycle: int) -> float:
    """
    Returns the current average volumetric water content [%].
    
    :param channel: Channel to be used.
    :type channel: int
    :param cycle: Amount of times the channel is read before calculating a mean.
    :type cycle: int

    :return: Current average volumetric water content in %.
    :rtype: float
    """
    # Scale voltage (0..3V) to volumetric water content (0..50%)
    totalMoisture = 0.0
    for x in range(cycle): # Return average value
        moisture = (readVoltage(channel) * 50.0) / 3.0
        totalMoisture += moisture
        time.sleep(1)
    return round(totalMoisture / cycle, 2) # auf 2 Nachkommastellen runden

def readTemperature(channel: int, cycle : int) -> float:
    """
    Returns the current average temperature [°C].
    
    :param channel: Channel to be used.
    :type channel: int
    :param cycle: Amount of times the channel is read before calculating a mean.
    :type cycle: int

    :return: Current average temperature in °C.
    :rtype: float
    """
    # Scale voltage (0..3V) to temperature (-20..85°C)
    totalTemperature = 0.0
    for x in range(cycle): # Return average value
        temperature = (readVoltage(channel) - 0.5) * 100.0
        totalTemperature += temperature
        time.sleep(1)
    return round(totalTemperature / cycle, 2) # auf 2 Nachkommastellen runden

def checkWatered(old: float, new: float) -> bool:
    """
    Checks if a plant has been watered recently by comparing moisture.

    :param old: Last moisture measurement.
    :type old: float
    :param new: Current moisture measurement.
    :type new: float

    :return: Returns true if moisture increased significantly.
    :rtype: bool
    """
    if new - old > THRESHOLD:
        return True
    else:
        return False
    
def checkDry(lastMeasurement: measurement, dbAdapterPlant: DBAdapterPlant) -> bool:
    """
    Checks if a plant turned dry by comparing moisture.

    :param lastMeasurement: Last moisture measurement.
    :type lastMeasurement: measurement
    :param dbAdapterPlant: Database adapter to access the measurements.
    :type dbAdapterPlant: DBAdapterPlant

    :return: Returns true if plant just turned dry.
    :rtype: bool
    """
    minMoisture = dbAdapterPlant.getMinMoisture(lastMeasurement.plantId)

    # Measurement is already flagged as dry
    if lastMeasurement.isDry == 1:
        return False
    
    # Compare moisture against minimum Moisture
    elif lastMeasurement.moisture <= minMoisture:
        return True
    else:
        return False

def saveMeasurement(dbAdapterMeasurement: DBAdapterMeasurement, dbAdapterPlant: DBAdapterPlant, threadStop: threading.Event):
    """
    Saves the current moisture and temperature measurements of all assigned channels every x minutes.
    
    :param dbAdapterMeasurement: Database adapter to access the measurements.
    :type dbAdapterMeasurement: DBAdapterMeasurement
    :param dbAdapterPlant: Database adapter to access the plants.
    :type dbAdapterPlant: DBAdapterPlant
    :param threadRun: Thread is running while this flag is true.
    :type threadRun: threading.Event
    """
    # Skip reading sensor data if not running on Jetson Nano
    if "tegra" in platform.release():

        # Set timout length depening on mode
        if MODE == "interval":
            sleep = SLEEP
        elif MODE == "debug":
            sleep = 2

        while not threadStop.is_set():
            # Wait interval time
            threadStop.wait(timeout=sleep)

            # Exit function early during shutdown
            if threadStop.is_set():
                break

            # Get all assigned input channels
            channels = dbAdapterPlant.getChannel("assigned")

            if not channels:
                # Skip saving measurements if no plants are assigned
                logging.info("No plants assigned to any channels. Saving measurement skipped.")
            else:
                # Save measurement for each assigned channel
                for ch in channels:
                    # Check if reading mode is interval or debug
                    if MODE == "interval":
                        # Check if recent measurement exists
                        watered = False; dry = False
                        lastMeasurement = dbAdapterMeasurement.getSingle(plant=ch.plantId, mode="recent")
                        if lastMeasurement is None:
                            logging.info("No recent measurement found. All checks skipped.")
                            
                        # Check if plant got watered since last measurement
                        elif checkWatered(lastMeasurement.moisture, readMoisture(ch.chMoisture, 1)):
                            logging.info("Watering detected.")
                            watered = True

                        # Check if plant dropped below minMoisture
                        elif checkDry(lastMeasurement, dbAdapterPlant):
                            logging.info("Plant turning dry detected.")
                            dry = True

                        # Set minutes until dry for all previous measurements
                        if watered or dry:
                            setMinutesUntilDry(ch.plantId, dbAdapterMeasurement, lastMeasurement)

                            # Train model using the now archived measurements
                            trainModel(ch.plantId, dbAdapterMeasurement)

                        # Skip insert after the plant was watered
                        # creates a little buffer while water spreads through the soil
                        if not watered:
                            # Format timestamp
                            now = datetime.now()
                            timestamp = now.strftime(FORMAT)

                            isDry = 0
                            # Plant has just been watered
                            if lastMeasurement is None:
                                isDry = 0

                            # Plant just turned dry or is already dry
                            elif dry or lastMeasurement.isDry:
                                isDry = 1

                            # Read moisture and temperature from SMT50 (-1 = non-archived entry)
                            moisture = readMoisture(ch.chMoisture, 5)
                            temperature = readTemperature(ch.chTemperature, 5)
                            dbAdapterMeasurement.insert(measurement(ch.plantId, moisture, temperature, -1, isDry, timestamp))
                    elif MODE == "debug":
                        # Print data directly
                        moistureV = readVoltage(ch.chMoisture)
                        moisture = readMoisture(ch.chMoisture, 1)
                        temperatureV = readVoltage(ch.chTemperature)
                        temperature = readTemperature(ch.chTemperature, 1)
                        print(f"Channel [{ch.channelId}] - Moisture: {moistureV:.2f}V = {moisture}%, Temperature: {temperatureV:.2f}V = {temperature}°C")

def setMinutesUntilDry(plantId: int, dbAdapter: DBAdapterMeasurement, recentMeasurement : measurement):
    """
    Set Minutes until Dry for all non-archived measurements of a plant.
    
    :param plantId: PlantID for which the Minutes until Dry are set.
    :type plantId: int
    :param dbAdapter: Database adapter to access the measurements.
    :type dbAdapter: DBAdapterMeasurement
    :param recentMeasurement: The most recent measurement.
    :type recentMeasurement: measurement
    """
    # Format recent timestamp
    recentTime = datetime.strptime(recentMeasurement.timestamp, FORMAT)

    for entry in dbAdapter.getList(plant=plantId, limit=-1, mode="current"):
        # Format current timestamp
        actTime = datetime.strptime(entry.timestamp, FORMAT)

        # Calculate minutes until dry
        sekUntilDry = recentTime - actTime
        minUntilDry = sekUntilDry.total_seconds() / 60.0

        # Update every measurement
        dbAdapter.update(entry.measureId, minUntilDry)
            
    # Logging
    logging.info("Minutes until dry set.")