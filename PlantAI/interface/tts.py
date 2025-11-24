"""
Description:
    Text-to-Speech (TTS) using Silero Models.
Author: Tim Grundey
Created: 24.11.2025
"""

import pyaudio
import torch
import wave
from system.loader import getConfig

# Configuration
DEVICE = getConfig("interface", "tts", "device")

# Load Silero TTS model
model_tts, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='en',
    speaker='v3_en'
)
