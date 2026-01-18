/*
Description:
    SQL Query for creating the SQLite3 database
Author: Tim Grundey
Created: 25.09.2025
*/

-- Create table for species
CREATE TABLE IF NOT EXISTS species (
    speciesId INTEGER PRIMARY KEY,
    name VARCHAR(40),
    minMoisture FLOAT
);

-- Add default entries for species
INSERT INTO species (name, minMoisture) VALUES
('Schefflera', 20.0),
('Azalee', 18.0);

-- Create table for plants
CREATE TABLE IF NOT EXISTS plants (
    plantId INTEGER PRIMARY KEY,
    speciesId INTEGER,
    name VARCHAR(40),
    location VARCHAR(10),
    FOREIGN KEY (speciesId) REFERENCES species(speciesId)
);

-- Create table for input channels
CREATE TABLE IF NOT EXISTS channel (
    channelId INTEGER PRIMARY KEY,
    plantId INTEGER,
    chMoisture INTEGER,
    chTemperature INTEGER,
    desc VARCHAR(40),
    FOREIGN KEY (plantId) REFERENCES plants(plantId) ON DELETE SET NULL
);

-- Add default entries for channels
INSERT INTO channel (chMoisture, chTemperature, desc) VALUES
(0, 1, 'ADS1115 Channel 0-1'),
(2, 3, 'ADS1115 Channel 2-3');

-- Create table for measurements
CREATE TABLE IF NOT EXISTS measurements (
    measureId INTEGER PRIMARY KEY,
    plantId INTEGER,
    moisture FLOAT,
    temperature FLOAT,
    minUntilDry INTEGER,
    isDry INTEGER,
    timestamp VARCHAR(15),
    FOREIGN KEY (plantId) REFERENCES plants(plantId)
);
