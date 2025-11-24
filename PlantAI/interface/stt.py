"""
Description:
    Speech-to-Text (STT) using Silero Models.
Author: Tim Grundey
Created: 24.11.2025
"""

import os
import torch
import wave
from system.loader import getConfig

# Configuration
SAMPLE_RATE = getConfig("interface", "vad", "sampleRate")
DEVICE = getConfig("interface", "stt", "device")

# Load Silero STT model
model_stt, decoder, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_stt',
    language='en',
    device=DEVICE
)
(read_batch, split_into_batches, read_audio, prepare_model_input) = utils

def convert(speech: bytes) -> str:
    # Save temporary wave file
    path = "PlantAI/resources/sound/tempSTT.wav"
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(speech)

    # Read temporary wave file and convert to text
    audio_tensor = read_audio(path)
    input_data = prepare_model_input([audio_tensor], device=DEVICE)
    output = model_stt(input_data)
    text = decoder(output[0])

    # Remove temporary file
    if os.path.exists(path):
        os.remove(path)

    return text.strip()