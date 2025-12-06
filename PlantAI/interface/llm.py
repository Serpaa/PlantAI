"""
Description:
    Large Language Model (LLM) provided by Ollama.
Author: Tim Grundey
Created: 26.11.2025
"""

import logging
from ollama import chat
from ollama import ChatResponse

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
            "- You are a helpful voice assistant."
            "- Answer in exactly one short sentence."
            "- Always use full words for numbers e.g. three, seven or sixty."
            "- No additional comments.")
    
    # Build user message
    if data is None:
        userContent = prompt
    else:
        userContent = f"'{prompt}' using additional information: '{data}'"

    # Send message to model
    response: ChatResponse = chat(model='llama3.2', messages=[
        {'role': 'system', 'content': sysContent},
        {'role': 'user', 'content': userContent}
    ])

    # Some logging
    logging.info(f"Prompt: {userContent}")
    logging.info(f"Response created: {response.message.content}")

    # Return response
    return response.message.content
