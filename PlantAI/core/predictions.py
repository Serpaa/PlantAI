"""
Description:
    Predicts in how many hours a plant has to be watered again using soil moisture and temperature.
Author: Tim Grundey
Created: 31.10.2025
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from core.models import measurement

def hoursUntilDry(allMeasurements: list[measurement]) -> int:
    # Fill lists with data
    listMinUntilDry = []; listMoisture = []
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

    # Split training and test data (80/20)
    # random_state makes sure the data is always mixed the same way (only for testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)

    # Create pipeline with random forest model
    pipe = Pipeline([
        ('model', RandomForestRegressor())
    ])

    # Train model with data
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    # Evaluation
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Prediction: {y_pred}")
    print(f"MAE: {mae:.3f}, R²: {r2:.3f}")

    # Visualisation
    plt.title("Predictions (using X test values)")
    plt.scatter(X_train, y_train)
    plt.scatter(X_test, y_pred, c='m')
    plt.ylabel("Minutes until dry")
    plt.xlabel("Moisture")
    plt.show()
