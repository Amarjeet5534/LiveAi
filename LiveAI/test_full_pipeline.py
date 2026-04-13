import asyncio
from voice.speech_to_text import record_audio, transcribe_audio
from voice.text_to_speech import speak
from config import model

print("🎤 Speak your question...")

record_audio(duration=6)
question = transcribe_audio()

print("📝 You said:", question)

if not question.strip():
    print("⚠ No speech detected.")
else:
    clean_prompt = f"""
Answer the following question in plain text.

Rules:
- Do NOT use markdown.
- Do NOT use asterisks (*).
- Do NOT use bold or formatting symbols.
- Keep it clean and readable.
- Keep it concise.

Question:
{question}
"""

    response = model.generate_content(clean_prompt)
    answer = response.text

    # Extra safety: remove any accidental markdown
    answer = answer.replace("*", "")

    print("🤖 Gemini:", answer)

    asyncio.run(speak(answer))
