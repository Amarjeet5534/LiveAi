#!/usr/bin/env python3
"""Quick verification that Ollama and voice system are working."""

import sys

print("🔍 System Check\n")

# Test 1: Check Ollama is running
print("1️⃣  Checking Ollama...")
try:
    import requests
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        print("   ✅ Ollama is running\n")
    else:
        print("   ❌ Ollama not responding\n")
        print("   👉 Start Ollama: ollama serve\n")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Ollama connection failed: {e}\n")
    print("   👉 Start Ollama: ollama serve\n")
    sys.exit(1)

# Test 2: Check microphone  
print("2️⃣  Checking microphone (device 18)...")
try:
    import sounddevice as sd
    device = sd.query_devices(18)
    print(f"   ✅ Mic found: {device['name']}\n")
except:
    print("   ⚠️  Mic device 18 not found\n")
    print("   To find your mic, run: python -c \"import sounddevice as sd; print(sd.query_devices())\"\n")

# Test 3: Quick Ollama response
print("3️⃣  Testing Ollama response...")
try:
    import ollama
    print("   Sending test message to Ollama...")
    response = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": "Say OK"}],
    )
    answer = response["message"]["content"].strip()
    print(f"   ✅ Ollama replied: {answer}\n")
except Exception as e:
    print(f"   ❌ Ollama error: {e}\n")
    sys.exit(1)

print("✅ All systems ready!\n")
print("Run: python main.py\n")
