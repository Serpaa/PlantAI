"""
Description:
    Voice activity detection (VAD) using Silero Models.
Author: Tim Grundey
Created: 22.11.2025
"""

import logging
import numpy as np
import pyaudio
import time
import wave
import interface.stt as stt
import interface.tts as tts
from silero_vad import load_silero_vad, get_speech_timestamps
from system.loader import getConfig

# Configuration
SAMPLE_RATE = getConfig("interface", "vad", "sampleRate")
CHUNK = getConfig("interface", "vad", "chunk")
PAUSE = getConfig("interface", "vad", "speechPause")
TIMEOUT = getConfig("interface", "vad", "wakewordTimeout")
WAKEWORD = getConfig("interface", "vad", "wakeword")

# Load Silero VAD model
model = load_silero_vad()

def detect():
    """Continously records audio and checks for voice."""
    speechDetected = False; lastSpeech = 0
    wakewordDetected = False; lastWakeword = 0
    listSpeech = []

    # Init PyAudio and open audio stream
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        output=True,
        frames_per_buffer=CHUNK)
    
    while not tts.active():
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
            # Combine all chunks as list
            listSpeech.append(audioChunk)

            # Log result and play audio
            if (not speechDetected):
                logging.info(f"Voice detected! Start recording ...")

            # Record time when speech was detected
            speechDetected = True
            lastSpeech = time.time()
        else:
            # Record current time
            now = time.time()

            # Detect when speech has ended
            # by comparing current time and last time speech was detected
            if speechDetected:
                if (now - lastSpeech) > PAUSE:
                    speechDetected = False

                    # Turn speech list into string
                    separator = b''
                    combinedSpeech = separator.join(listSpeech)
                    listSpeech.clear()

                    # Hand over raw speech to STT
                    convertedSpeech = stt.convert(combinedSpeech)

                    # Choose if speech is wakeword or command
                    if wakewordDetected:
                        wakewordDetected = False
                        logging.info(f"Command recorded: {convertedSpeech}")
                    else:
                        logging.info(f"Wakeword recorded: {convertedSpeech}")

                        # Detect wakeword
                        if WAKEWORD in convertedSpeech:
                            # Record time when wakeword was detected
                            wakewordDetected = True
                            lastWakeword = time.time()

                            # Play activation sound
                            play('PlantAI/resources/sound/activate.wav')
                            logging.info(f"Wakeword detected! Waiting for command ...")
            elif wakewordDetected:
                # Reset wakeword after timeout
                if (now - lastWakeword) > TIMEOUT:
                    wakewordDetected = False
                    logging.warning(f"Command timeout after {TIMEOUT}s")

    # Close audio stream
    stream.close()
    pa.terminate()

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
