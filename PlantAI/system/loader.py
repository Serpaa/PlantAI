"""
Description:
    Loads the config file and returns specific entries
Author: Tim Grundey
Created: 14.10.2025
"""

import yaml

def getConfig(dir1: str, dir2: str):
    """Returns a value stored in the config file under a certain path."""
    with open("PlantAI/system/config.yaml") as stream:
        config = yaml.safe_load(stream)
        return config[dir1][dir2]
