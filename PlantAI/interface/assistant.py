"""
Description:
    Voice assistant waits for keywords and responds using the LLM.
Author: Tim Grundey
Created: 05.12.2025
"""

import interface.audio as audio
import interface.llm as llm
from datetime import datetime
from api.weather import getForecast
from core.measurements import readMoisture
from core.predictions import predictTimeUntilDry

def respond(speech: str):
    """
    Creates a voice response for different commands using the LLM.
    
    :param speech: Command to be used.
    :type speech: str
    """
    if "time" in speech:
        # Get current time
        time = datetime.now()
        hrs = time.strftime("%H")
        min = time.strftime("%M")
        
        data = f"Current time: {hrs} o'clock and {min} minutes."
        prompt = speech
    elif "water" in speech:
        # Get time until dry
        days, hours = predictTimeUntilDry(readMoisture(1))

        # Only create answer if prediction was made
        if days == None and hours == None:
            data = None
            prompt = "Tell the user not enough data has been collected to predict the moisture."
        else:
            data = f"Time until plant has to be watered again: {days} days and {hours} hours."
            prompt = speech
    elif "weather" in speech:
        # Get weather forecast
        data = getForecast()
        prompt = speech
    else:
        # Unknown command
        data = None
        prompt = "Tell the user you apologize and can't help with that."

    # Send speech to LLM and respond
    response = llm.question(prompt, data)
    audio.tts(response)
