import asyncio
import subprocess
import webbrowser
import ollama
import re
import os

from voice.speech_to_text import record_audio, transcribe_audio
from voice.text_to_speech import speak
from control import click, scroll_down, scroll_up, type_text
from screen import analyze_screen


print("🚀 Neura AI Agent Started")


# ==========================
# CLEAN TEXT
# ==========================
def clean_text(text):
    return re.sub(r"[^\w\s]", "", text).lower().strip()


# ==========================
# OPEN APP (FIXED)
# ==========================
def open_app(app):

    app = clean_text(app)

    aliases = {
        "vs": "vscode",
        "vs code": "vscode",
        "visual studio code": "vscode",
        "note": "notepad",
        "note pad": "notepad",
        "calculator": "calc",
        "calc": "calc"
    }

    if app in aliases:
        app = aliases[app]

    # Notepad / Calc
    if app == "notepad":
        subprocess.Popen("notepad.exe")
        return True

    if app == "calc":
        subprocess.Popen("calc.exe")
        return True

    # Chrome
    if app == "chrome":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        for p in paths:
            if os.path.exists(p):
                subprocess.Popen(p)
                return True

    # VS Code
    if app == "vscode":
        path = os.path.expandvars(
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        )
        if os.path.exists(path):
            subprocess.Popen(path)
            return True

    # fallback (windows search)
    try:
        subprocess.Popen(f'start "" "{app}"', shell=True)
        return True
    except:
        return False


# ==========================
# AI RESPONSE
# ==========================
def ask_ai(question):

    response = ollama.chat(
        model="phi3",
        messages=[
            {
                "role": "system",
                "content": "You must answer in EXACTLY ONE short sentence. Maximum 10 words. Be very brief."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        stream=False
    )

    answer = response["message"]["content"].strip()
    
    # Force max 15 words
    words = answer.split()[:15]
    return " ".join(words)


# ==========================
# INTENT CLASSIFIER (BRAIN)
# ==========================
def classify_intent(text):
    """Fast intent detection - checks command at start of text."""
    
    text_lower = text.lower().strip()
    
    # APP COMMANDS - "open X"
    if text_lower.startswith("open") or text_lower.startswith("launch") or text_lower.startswith("start"):
        return "app"
    
    # WEB SEARCH - "search X" or "google X" or "youtube X"
    if text_lower.startswith("search") or text_lower.startswith("google") or "youtube" in text_lower:
        return "web"
    
    # MOUSE/KEYBOARD
    if "click" in text_lower or "scroll" in text_lower:
        return "mouse"
    
    if text_lower.startswith("type"):
        return "keyboard"
    
    # SCREEN VISION
    if "screen" in text_lower or "analyze" in text_lower or "what" in text_lower:
        return "vision"
    
    # Default to chat
    return "chat"


# ==========================
# MAIN LOOP
# ==========================
async def assistant_loop():

    print("🎤 Ready! Say 'open chrome', 'search weather', 'click', or ask a question...")
    print("Say 'terminate' to exit.\n")

    while True:

        print("🎧 Listening (5 seconds or until silent)...")
        record_audio(duration=5)  # BETTER: 5 sec for full sentences

        text = transcribe_audio()

        print("📝 You:", text)

        if not text:
            print("⚠️  No speech detected. Try again.\n")
            continue

        text = clean_text(text)
        
        print(f"✓ Processing: {text}")

        # EXIT
        if "terminate" in text:
            await speak("Shutting down")
            break

        intent = classify_intent(text)
        print(f"🎯 Intent: {intent}\n")

        # ================= APP =================
        if intent == "app":

            app = text.replace("open", "").replace("launch", "").replace("start", "").strip()

            if open_app(app):
                msg = f"Opening {app}"
                print(f"✅ {msg}")
                try:
                    await speak(msg)
                except:
                    pass
            else:
                msg = "Application not found"
                print(f"❌ {msg}")
                try:
                    await speak(msg)
                except:
                    pass

            continue

        # ================= WEB =================
        if intent == "web":

            query = text.replace("search", "").replace("google", "").strip()

            webbrowser.open(
                "https://www.google.com/search?q=" + query
            )
            
            msg = f"Searching"
            print(f"🌐 {msg}")
            try:
                await speak(msg)
            except:
                pass

            continue

        # ================= MOUSE =================
        if intent == "mouse":

            if "click" in text:
                click()

            elif "scroll down" in text:
                scroll_down()

            elif "scroll up" in text:
                scroll_up()

            msg = "Done"
            print(f"🖱️  {msg}")
            try:
                await speak(msg)
            except:
                pass

            continue

        # ================= KEYBOARD =================
        if intent == "keyboard":

            content = text.replace("type", "").strip()

            type_text(content)

            msg = f"Typed"
            print(f"⌨️  {msg}")
            try:
                await speak(msg)
            except:
                pass

            continue

        # ================= SCREEN =================
        if intent == "vision":

            print("📹 Analyzing screen...")
            answer = analyze_screen(text)

            print("🤖 Neura:", answer)

            try:
                await speak(answer)
            except:
                pass

            continue

        # ================= AI CHAT =================
        print("🤖 Thinking...")
        answer = ask_ai(text)

        if answer:
            print("🤖 Neura:", answer)
            try:
                await speak(answer)
            except Exception as e:
                print(f"⚠️  TTS Error: {e}")
        print()


# ==========================
# RUN
# ==========================
asyncio.run(assistant_loop())
