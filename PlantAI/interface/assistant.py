"""
Description:
    Voice assistant waits for keywords and responds using the LLM.
Author: Tim Grundey
Created: 05.12.2025
"""

import interface.audio as audio
import interface.llm as llm
from datetime import datetime
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
        time = datetime.now().strftime("%H:%M")
        data = f"Current time: {time}"
        prompt = speech
    elif "water" in speech:
        # Get days until watered
        days, hours = predictTimeUntilDry(readMoisture(1))
        data = f"Time until plant has to be watered again: {days} days and {hours} hours."
        prompt = speech
    else:
        # Unknown command
        data = None
        prompt = "Tell the user you apologize and can't help with that."

    # Send speech to LLM and respond
    response = llm.question(prompt, data)
    audio.tts(response)
