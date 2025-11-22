"""
Description:
    Voice activity detection (VAD) using Silero Models.
Author: Tim Grundey
Created: 22.11.2025
"""

import logging
import numpy as np
import pyaudio
import wave
from silero_vad import load_silero_vad, get_speech_timestamps
from system.loader import getConfig

# Configuration
SAMPLE_RATE = getConfig("vad", "sampleRate")
CHUNK = getConfig("vad", "chunk")

# Load Silero VAD model
model = load_silero_vad()

def detect():
    """Continously records audio and checks for voice."""
    # Init PyAudio and open audio stream
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK)
    
    while True:
        # Seperate audio into chunks
        audioChunk = stream.read(num_frames=SAMPLE_RATE, exception_on_overflow=False)

        # Convert raw audio chunk into float [-1..1]
        data = np.frombuffer(audioChunk, np.int16).astype(np.float32) / 32768.0

        # Check audio for voice and return timestamps
        speech = get_speech_timestamps(
            data,
            model,
            sampling_rate=SAMPLE_RATE,
            return_seconds=False)

        # Voice has been detected
        if len(speech) > 0:
            # Read start and end frame
            startFrame = speech[0]["start"]
            endFrame = speech[0]["end"]

            # Log result and play audio
            logging.info(f"Voice detected - Frame: {startFrame} - {endFrame}")
            play('PlantAI/resources/sound/activate.wav')

    # Close audio stream
    stream.close()
    p.terminate()

def play(path: str):
    """Plays the wave file located at the selected path."""
    with wave.open(path, 'rb') as wf:
        # Init PyAudio and open audio stream
        pa = pyaudio.PyAudio()
        stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        # Play samples from the wave file
        while len(data := wf.readframes(CHUNK)):
            stream.write(data)

        # Close audio stream
        stream.close()
        pa.terminate()
