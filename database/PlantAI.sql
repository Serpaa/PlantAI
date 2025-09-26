CREATE TABLE IF NOT EXISTS species (
    species_id INTEGER PRIMARY KEY,
    name VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS sensors (
    sensor_id INTEGER PRIMARY KEY,
    serial_no VARCHAR(40)
);

CREATE TABLE IF NOT EXISTS plants (
    plant_id INTEGER PRIMARY KEY,
    name VARCHAR(40),
    species INTEGER,
    sensor INTEGER,
    FOREIGN KEY (species) REFERENCES species(species_id),
    FOREIGN KEY (sensor) REFERENCES sensors(sensor_id)
);

CREATE TABLE IF NOT EXISTS moisture (
    moisture_id INTEGER PRIMARY KEY,
    plant INTEGER,
    value FLOAT,
    timestamp datetime,
    FOREIGN KEY (plant) REFERENCES plants(plant_id)
);

-- Add some data for testing
INSERT INTO plants (name, species, sensor) VALUES 
('Aloe Vera', 1, 1),
('Basil', 2, 2),
('Cactus', 3, 3);