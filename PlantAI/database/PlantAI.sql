/*
Description:
    SQL Query for creating the SQLite3 database
Author: Tim Grundey
Created: 25.09.2025
*/

CREATE TABLE IF NOT EXISTS species (
    speciesId INTEGER PRIMARY KEY,
    name VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS sensors (
    sensorId INTEGER PRIMARY KEY,
    i2cAddress INTEGER
);

CREATE TABLE IF NOT EXISTS plants (
    plantId INTEGER PRIMARY KEY,
    speciesId INTEGER,
    sensorId INTEGER,
    name VARCHAR(40),
    FOREIGN KEY (speciesId) REFERENCES species(speciesId),
    FOREIGN KEY (sensorId) REFERENCES sensors(sensorId)
);

CREATE TABLE IF NOT EXISTS measurements (
    measureId INTEGER PRIMARY KEY,
    sensorId INTEGER,
    moisture FLOAT,
    temperature FLOAT,
    timestamp datetime,
    FOREIGN KEY (sensorId) REFERENCES sensors(sensorId)
);
