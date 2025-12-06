"""
Description:
    Predicts in how many hours a plant has to be watered again using soil moisture and temperature.
Author: Tim Grundey
Created: 31.10.2025
"""

import logging
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from database.adapter import DBAdapterMeasurement

# Prepare pipeline
pipe = Pipeline([
    ('model', RandomForestRegressor())
])

def trainModel(dbAdapter : DBAdapterMeasurement):
    # Fill lists with all archived measurements
    listMinUntilDry = []; listMoisture = []
    allMeasurements = dbAdapter.getList(1, -1, "archived")

    # Skip training if no archived measurements are returned
    if len(allMeasurements) > 0:
        for measurement in allMeasurements:
            listMinUntilDry.append(measurement.minUntilDry)
            listMoisture.append(measurement.moisture)

        # Create dictionary from lists
        data = {
            'minUntilDry': listMinUntilDry,
            'moisture': listMoisture
        }

        # Convert List into DataFrame and prepare features
        df = pd.DataFrame(data)
        X = df[['moisture']]
        y = df['minUntilDry']

        # Save DataFrame as png
        # plot(df)

        # Split training and test data (80/20)
        # random_state makes sure the data is always mixed the same way (only for testing)
        X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state=42)

        # Train model with data
        pipe.fit(X_train, y_train)
        logging.info(f"Random Forest Model trained with {len(allMeasurements)} measurements.")

        # Create evaluation
        evaluation(X_test, y_test)
    else:
        logging.warning(f"Random Forest Model training skipped, no archived measurements found.")

def evaluation(X_test : list, y_test : list):
    # Make predictions for testing split
    y_pred = pipe.predict(X_test)

    # Evaluate and log results
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    logging.info(f"Evaluation - MAE: {mae:.3f}, R²: {r2:.3f}")

def predictTimeUntilDry(curMoisture : float) -> int:
    """Returns the days:hours it takes until the plant is dry and has to be watered again."""
    # Create dataframe and make prediction
    data = pd.DataFrame({'moisture': [curMoisture]})
    prediction = pipe.predict(data)

    # Convert minutes to days and hours
    time = timedelta(minutes=prediction[0])
    days = time.days
    hours = round(time.seconds / 3600)

    # Log and return result
    logging.info(f"Prediction - {curMoisture}%: Water in {days} days and {hours} hours.")
    print(f"Prediction - {curMoisture}%: Water in {days} days and {hours} hours.")
    return days, hours

def plot(df : pd.DataFrame):
    """Saves the DataFrame as a PNG."""
    # Create plot from DataFrame
    plt.figure(figsize=(12, 5), dpi=250)
    plt.plot(df["minUntilDry"], df["moisture"])
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
