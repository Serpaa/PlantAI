"""
Description:
    Predicts in how many hours a plant has to be watered again using soil moisture and temperature.
Author: Tim Grundey
Created: 31.10.2025
"""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from joblib import dump, load
from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from database.adapter import DBAdapterMeasurement
from system.streams import importConfigFromYAML

# Configuration
stream = importConfigFromYAML()
config = stream["core"]["predictions"]

# Constants
SCATTER = config["createScatter"]

def trainModel(plantId: int, dbAdapter : DBAdapterMeasurement):
    """
    Trains the model of a plant using the archived measurements, skips if no archived measurements are found.
    
    :param plantId: Measurements of this PlantID are used to train the model.
    :type plantId: int
    :param dbAdapter: Database adapter to access the measurements.
    :type dbAdapter: DBAdapterMeasurement
    """
    # Fill lists with all archived measurements
    listMinUntilDry = []; listMoisture = []; listIsDry = []
    allMeasurements = dbAdapter.getList(plantId, -1, "all")

    # Skip training if no archived measurements are returned
    if len(allMeasurements) > 0:
        for measurement in allMeasurements:
            listMinUntilDry.append(measurement.minUntilDry)
            listMoisture.append(measurement.moisture)
            listIsDry.append(measurement.isDry)

        # Create dictionary from lists
        data = {
            'minUntilDry': listMinUntilDry,
            'moisture': listMoisture,
            'isDry': listIsDry
        }

        # Convert List into DataFrame
        df = pd.DataFrame(data)

        # Calculate moisture slope
        df["moistureSlope"] = (
            df["moisture"]
            .rolling(window=10, min_periods=10)
            .apply(rollingSlope, raw=True)
        )

        # Calculate relative moisture
        df["moistureRelative"] = df["moisture"] / df["moisture"].rolling(100).max()

        # Prepare features and target
        X = df[['moisture', 'moistureSlope', 'moistureRelative', 'isDry']]
        y = df['minUntilDry']

        # Save DataFrame as png
        if (SCATTER):
            plot(df)

        # Split training and test data (80/20)
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2)

        # Prepare pipeline
        pipe = Pipeline([
            ('model', RandomForestRegressor())
        ])

        # Train model with data
        pipe.fit(X_train, y_train)
        logging.info(f"Plant {plantId}: Random Forest Model trained with {len(allMeasurements)} measurements.")

        # Save model to persistence
        dump(pipe, f"PlantAI/resources/models/pipeline_{plantId}.joblib")

        # Create evaluation
        evaluation(pipe, X_test, y_test)
    else:
        logging.warning(f"Plant {plantId}: Random Forest Model training skipped, no archived measurements found.")

def evaluation(pipe: Pipeline, X_test : list, y_test : list):
    """
    Logs an evaluation of the model.
    
    :param pipe: Pipeline used for the evaluation.
    :type pipe: Pipeline
    :param X_test: X test values.
    :type X_test: list
    :param y_test: Y test values.
    :type y_test: list
    """
    # Make predictions for testing split
    y_pred = pipe.predict(X_test)

    # Evaluate and log results
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    logging.info(f"Evaluation - MAE: {mae:.3f}, R²: {r2:.3f}")

def predictTimeUntilDry(plantId: int, dbAdapter : DBAdapterMeasurement) -> int:
    """
    Returns the days:hours it takes until the plant is dry and has to be watered again.
    
    :param plantId: Plant for which to make the prediction.
    :type plantId: int
    :param dbAdapter: Database adapter to access the measurements.
    :type dbAdapter: DBAdapterMeasurement

    :return: Days and hours until the plant is dry. Returns none if no prediction could be made.
    :rtype: int, int
    """
    try:
        # Load Pipeline from persistence
        pipe: Pipeline = load(f"PlantAI/resources/models/pipeline_{plantId}.joblib")
    except FileNotFoundError as ex:
        # Return none if Pipeline doesn't exist
        logging.error(f"Prediction failed: {ex}")
        return None, None
    
    # Get recent measurements
    measurements = dbAdapter.getList(plantId, 100, "all")
    moistureArray = np.array([msr.moisture for msr in measurements])
    curMoisture = measurements[-1].moisture
    curIsDry = measurements[-1].isDry

    if curIsDry:
        # Log and return result if plant is dry
        logging.info(f"Plant {plantId} - {curMoisture}% moisture")
        logging.info(f"Prediction - Plant is dry, water as soon as possible!")
        return -1, -1
    else:
        # Calculate moisture slope
        moistureSlope = rollingSlope(moistureArray[-10:])

        # Calculate relative moisture
        dfr = pd.DataFrame({"moisture": moistureArray})
        dfr["moistureRelative"] = dfr["moisture"] / dfr["moisture"].rolling(100).max()
        moistureRelative = dfr.iloc[-1]["moistureRelative"]

        # Build dataframe
        df = pd.DataFrame({
            "moisture": [curMoisture],
            "moistureSlope": [moistureSlope],
            "moistureRelative": [moistureRelative],
            "isDry": [curIsDry]
            })

        try:
            # Make prediction
            prediction = pipe.predict(df)
        except NotFittedError as ex:
            # Return none if Pipeline hasn't been fitted yet
            logging.error(f"Prediction failed: {ex}")
            return None, None

        # Convert minutes to days and hours
        time = timedelta(minutes=prediction[0])
        days = time.days
        hours = round(time.seconds / 3600)

        # Log and return result
        logging.info(f"Plant {plantId} - {curMoisture}% moisture, {round(moistureSlope, 2)} slope, {round(moistureRelative, 2)} relative moisture")
        logging.info(f"Prediction - Water in {days} days and {hours} hours.")
        return days, hours

def rollingSlope(y):
    """
    Creates a linear polynom minimising the squared error through all values.

    :param y: Values of the linear polynom.
    :type y: array_like

    :return: Highest degree coefficient (slope).
    :rtype: float
    """
    window = len(y)
    x = np.arange(window) # build array of x values
    poly = np.polyfit(x, y, 1) # create first degree polynom (linear)
    return poly[0]

def plot(df: pd.DataFrame):
    """
    Exports the DataFrame as a PNG image.
    
    :param df: Dataframe to be saved.
    :type df: DataFrame
    """
    # Create scatter plot from DataFrame
    plt.figure(figsize=(12, 5), dpi=250)
    plt.scatter(df["minUntilDry"], df["moisture"], s=10)
    plt.xlabel("Minutes until Dry")
    plt.ylabel("Moisture")
    plt.title("Measurements")
    plt.tight_layout()

    # Format and create timestamp
    format = "%Y%m%d_%H%M%S"
    now = datetime.now()
    timestamp = now.strftime(format)

    # Save plot as PNG
    plt.savefig(f"PlantAI/system/moisture_{timestamp}.png")
