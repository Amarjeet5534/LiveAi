import asyncio
import edge_tts
import os
import pygame
import sounddevice as sd
import numpy as np

VOICE = "en-IN-PrabhatNeural"

pygame.mixer.init()

async def speak(text):
    os.makedirs("data/audio", exist_ok=True)
    file_path = "data/audio/output.mp3"

    # Stop previous playback
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    # Generate speech
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(file_path)

    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    print("🔊 Speaking... (you can interrupt)")

    fs = 16000
    chunk_size = int(fs * 0.3)

    with sd.InputStream(samplerate=fs, channels=1, dtype="int16") as stream:
        while pygame.mixer.music.get_busy():
            chunk, _ = stream.read(chunk_size)
            volume = np.abs(chunk).mean()

            # If user speaks → interrupt
            if volume > 600:   # interrupt threshold
                print("🛑 Interrupt detected!")
                pygame.mixer.music.stop()
                break

            await asyncio.sleep(0.1)
