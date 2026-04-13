import asyncio
import subprocess
import webbrowser
import ollama

from voice.speech_to_text import record_audio, transcribe_audio
from voice.text_to_speech import speak

from memory import save_memory, memory_context
from control import click, scroll_down, scroll_up, type_text
from screen import analyze_screen


print("🚀 Neura AI Agent Started")


def open_app(app):

    try:
        subprocess.Popen(f"start {app}", shell=True)
        return True
    except:
        return False


def ask_ai(question):

    context = memory_context()

    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "system",
                "content": "Answer briefly."
            },
            {
                "role": "user",
                "content": context + question
            }
        ]
    )

    return response["message"]["content"]


async def assistant_loop():

    while True:

        record_audio()

        text = transcribe_audio()

        print("You:", text)

        text = text.lower()

        if "terminate" in text:
            await speak("Shutting down")
            break

        if text.startswith("open"):

            app = text.replace("open", "").strip()

            if open_app(app):
                await speak("Opening " + app)
            else:
                await speak("I cannot open that")

            continue

        if text.startswith("search"):

            query = text.replace("search", "").strip()

            webbrowser.open(
                "https://www.google.com/search?q=" + query
            )

            await speak("Searching")

            continue

        if "click" in text:
            click()
            await speak("Clicking")
            continue

        if "scroll down" in text:
            scroll_down()
            await speak("Scrolling down")
            continue

        if "scroll up" in text:
            scroll_up()
            await speak("Scrolling up")
            continue

        if text.startswith("type"):

            content = text.replace("type", "").strip()

            type_text(content)

            continue

        if "what is on my screen" in text:

            answer = analyze_screen(text)

            print("Neura:", answer)

            await speak(answer)

            continue

        answer = ask_ai(text)

        print("Neura:", answer)

        await speak(answer)

        save_memory(text, answer)


asyncio.run(assistant_loop())
