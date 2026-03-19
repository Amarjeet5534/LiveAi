import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

# ==========================
# MICROPHONE SETTINGS
# ==========================

MIC_DEVICE = 18
AUDIO_FILE = "input.wav"

# Detect correct microphone sample rate automatically
device_info = sd.query_devices(MIC_DEVICE, "input")
SAMPLE_RATE = int(device_info["default_samplerate"])

print("🎤 Using mic:", device_info["name"])
print("🎧 Sample rate:", SAMPLE_RATE)

# ==========================
# LOAD WHISPER (FAST MODEL)
# ==========================

model = WhisperModel(
    "tiny.en",      # MUCH faster
    device="cpu",
    compute_type="int8"
)

# ==========================
# RECORD AUDIO
# ==========================

def record_audio(duration=4):

    print("🎤 Listening... Speak clearly")

    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        device=MIC_DEVICE
    )

    sd.wait()

    recording = recording.flatten()

    write(AUDIO_FILE, SAMPLE_RATE, recording)

    print("✅ Recording saved")

# ==========================
# TRANSCRIBE AUDIO
# ==========================

def transcribe_audio():

    print("🧠 Transcribing...")

    segments, _ = model.transcribe(
        AUDIO_FILE,
        beam_size=1,
        language="en"
    )

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()


# ==========================
# LIST MICROPHONES
# ==========================

def list_microphones():
    print(sd.query_devices())
