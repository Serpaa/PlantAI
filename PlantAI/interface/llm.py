"""
Description:
    Large Language Model (LLM) provided by Ollama.
Author: Tim Grundey
Created: 26.11.2025
"""

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
            "- Answer in exactly one short sentence."
            "- No additional comments.")
    
    # Build user message
    userContent = f"'{prompt}' using current time: '{data}' "

    # Send message to model
    response: ChatResponse = chat(model='llama3.2', messages=[
        {'role': 'system', 'content': sysContent},
        {'role': 'user', 'content': userContent}
    ])

    # Return response
    return response.message.content
