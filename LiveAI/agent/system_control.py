import os
import webbrowser


def open_app(app_name):
    app_name = app_name.lower()

    if "chrome" in app_name:
        os.system("start chrome")
        return "Opening Chrome."

    if "code" in app_name or "vs code" in app_name:
        os.system("start code")
        return "Opening Visual Studio Code."

    if "notepad" in app_name:
        os.system("start notepad")
        return "Opening Notepad."

    return "Application not recognized."


def shutdown_pc():
    os.system("shutdown /s /t 5")
    return "Shutting down the computer in 5 seconds."


def search_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)
    return f"Searching YouTube for {query}."


def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching Google for {query}."


def create_file(filename, content):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {filename} created successfully."
    except Exception as e:
        return f"Failed to create file: {str(e)}"
