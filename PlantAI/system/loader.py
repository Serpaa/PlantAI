"""
Description:
    Loads the yaml config file and returns the stream.
Author: Tim Grundey
Created: 14.10.2025
"""

import yaml

def getConfig():
    """Returns the config stream."""
    with open("PlantAI/resources/config.yaml") as stream:
        return yaml.safe_load(stream)
