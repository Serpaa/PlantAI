"""
Description:
    Large Language Model (LLM) provided by Ollama.
Author: Tim Grundey
Created: 26.11.2025
"""

import re
from ollama import chat
from ollama import ChatResponse
from num2words import num2words

def question(prompt: str, data) -> str:
    """
    Ask the Ollama LLM a question and return a response.
    
    :param prompt: Prompt for the LLM.
    :type prompt: str

    :return: Response from the LLM.
    :rtype: str
    """

    # Build system message with rules
    sysContent = (
        "System rules (follow these strictly):"
            "- You are a voice assistant."
            "- Answer in exactly one short sentence."
            "- No additional comments.")
    
    # Build user message
    userContent = f"'{prompt}' using additional information: '{data}' "

    # Send message to model
    response: ChatResponse = chat(model='llama3.2', messages=[
        {'role': 'system', 'content': sysContent},
        {'role': 'user', 'content': userContent}
    ])

    # Convert all numbers to words and return
    return re.sub(r'\d+', lambda m: num2words(int(m.group())), response.message.content)
