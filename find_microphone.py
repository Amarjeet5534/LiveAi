"""Find the correct microphone device."""

import sounddevice as sd
import numpy as np

print("🎤 All available audio devices:\n")
print("=" * 80)
devices = sd.query_devices()

for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:  # Only input devices
        marker = " ← CURRENT" if i == 18 else ""
        print(f"{i}: {device['name']}")
        print(f"   Input channels: {device['max_input_channels']}")
        print(f"   Sample rate: {device['default_samplerate']}")
        print(marker)
        print()

print("=" * 80)
print("\nTesting microphone device 18...\n")

try:
    device_info = sd.query_devices(18, "input")
    print(f"Using device: {device_info['name']}")
    print(f"Sample rate: {device_info['default_samplerate']}")
    print(f"Channels: {device_info['max_input_channels']}\n")
    
    print("🎤 Recording 3 seconds of audio...")
    fs = int(device_info["default_samplerate"])
    duration = 3
    
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32", device=18)
    sd.wait()
    
    # Calculate volume
    volume = np.abs(recording).mean()
    print(f"✅ Recording complete!")
    print(f"   Volume level: {volume:.4f}")
    
    if volume < 0.01:
        print("   ⚠️  Very quiet - check microphone or try a different device")
    elif volume > 0.5:
        print("   ✅ Good volume level!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTry a different device number. Examples:")
    print("- Change MIC_DEVICE = 18 to another number in voice/speech_to_text.py")
    print("- Or update main.py to use a different device")
