import asyncio
import edge_tts
import os
import pygame
import sounddevice as sd
import numpy as np
import threading

VOICE = "en-US-GuyNeural"

pygame.mixer.init()


def monitor_microphone():
    fs = 16000
    chunk_size = int(fs * 0.3)

    with sd.InputStream(samplerate=fs, channels=1, dtype="int16") as stream:
        baseline_chunks = []
        for _ in range(5):
            chunk, _ = stream.read(chunk_size)
            baseline_chunks.append(np.abs(chunk).mean())

        baseline = sum(baseline_chunks) / len(baseline_chunks)
        threshold = baseline * 3

        print(f"🎧 Interrupt threshold: {threshold:.2f}")

        while pygame.mixer.music.get_busy():
            chunk, _ = stream.read(chunk_size)
            volume = np.abs(chunk).mean()

            if volume > threshold:
                print("🛑 Interrupt detected!")
                pygame.mixer.music.stop()
                break


async def speak(text):
    os.makedirs("data/audio", exist_ok=True)
    file_path = "data/audio/output.mp3"

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()

    pygame.mixer.music.unload()

    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(file_path)

    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    print("🔊 Speaking... (say something to interrupt)")

    mic_thread = threading.Thread(target=monitor_microphone)
    mic_thread.start()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    mic_thread.join()
