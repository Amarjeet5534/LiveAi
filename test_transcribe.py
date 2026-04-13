from voice.speech_to_text import record_audio, transcribe_audio

record_audio(duration=8)
text = transcribe_audio()

print("📝 Transcribed Text:", text)
