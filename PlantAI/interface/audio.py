"""
Description:
    Audio control using Silero Models:
        - Voice activity detection (VAD)
        - Speech-to-Text (STT) conversion
        - Text-to-Speech (TTS) conversion
Author: Tim Grundey
Created: 26.11.2025
"""

import logging
import numpy as np
import os
import pyaudio
import time
import wave
from silero import silero_stt, silero_tts
from silero_vad import load_silero_vad, get_speech_timestamps
from system.loader import getConfig

# Configuration
SAMPLE_RATE = getConfig("interface", "vad", "sampleRate")
CHUNK = getConfig("interface", "vad", "chunk")
PAUSE = getConfig("interface", "vad", "speechPause")
TIMEOUT = getConfig("interface", "vad", "wakewordTimeout")
WAKEWORD = getConfig("interface", "vad", "wakeword")
DEVICE_TTS = getConfig("interface", "tts", "device")
DEVICE_STT = getConfig("interface", "stt", "device")

# Load Silero models
# Voice activity detection
model = load_silero_vad()

# Save current directory
# Move to resources for saving Silero config
cwd = os.getcwd()
os.chdir("PlantAI/resources")

# Speech-to-Text
model_stt, decoder, utils = silero_stt(
    language='en'
)

# Text-to-Speech
model_tts, example_text = silero_tts(
    language='en',
    speaker='v3_en',
)

# Return to previous directory
os.chdir(cwd)

# Get STT utils
(read_batch, split_into_batches, read_audio, prepare_model_input) = utils

# Set device (GPU or CPU)
model_tts.to(DEVICE_TTS)
model_stt.to(DEVICE_STT)

def vad():
    """
    Records audio and checks for voice activity.
    """
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
                    convertedSpeech = stt(combinedSpeech)

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
                            tts("Hello Tim!")
                            logging.info(f"Wakeword detected! Waiting for command ...")
            elif wakewordDetected:
                # Reset wakeword after timeout
                if (now - lastWakeword) > TIMEOUT:
                    wakewordDetected = False
                    logging.warning(f"Command timeout after {TIMEOUT}s")

    # Close audio stream
    stream.close()
    pa.terminate()

def stt(speech: bytes) -> str:
    """
    Speech-to-Text conversion using a temporary wave file.
    
    :param speech: Raw speech to be converted.
    :type speech: bytes
    """

    # Save temporary wave file
    path = "PlantAI/resources/sound/tempSTT.wav"
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(speech)

    # Read temporary wave file and convert to text
    audio_tensor = read_audio(path)
    input_data = prepare_model_input([audio_tensor], device=DEVICE_STT)
    output = model_stt(input_data)
    text = decoder(output[0])

    # Remove temporary file
    if os.path.exists(path):
        os.remove(path)

    return text.strip()

def tts(text: str):
    """
    Text-to-Speech conversion using a temporary wave file.
    
    :param text: Text to be converted.
    :type text: str
    """
    # Save temporary wave file
    path = "PlantAI/resources/sound/tempTTS.wav"
    model_tts.save_wav(
        text=text,
        speaker='en_0',
        sample_rate=24000,
        audio_path=path
    )

    # Play audio
    play(path)

    # Remove temporary file
    if os.path.exists(path):
        os.remove(path)

def play(path: str):
    """
    Plays the wave file located at the selected path.
    
    :param path: Path to the wave file.
    :type path: str
    """
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
