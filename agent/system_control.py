import os
import webbrowser
import subprocess


def open_app(app_name):
    """Open an application by name."""
    app_name = app_name.lower().strip()
    
    print(f"🔓 Attempting to open: {app_name}")
    
    # Aliases for common app names
    aliases = {
        "chrome": "chrome",
        "google chrome": "chrome",
        "code": "code",
        "vs code": "code",
        "visual studio code": "code",
        "vscode": "code",
        "notepad": "notepad",
        "note": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt"
    }
    
    if app_name in aliases:
        app_name = aliases[app_name]
    
    # Try direct Windows command
    try:
        if app_name == "chrome":
            # Try common Chrome paths
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            for path in paths:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    return f"Opening Chrome."
            # Fallback to system search
            os.system("start chrome")
            return "Opening Chrome."
        
        elif app_name == "code":
            os.system("start code")
            return "Opening Visual Studio Code."
        
        elif app_name == "notepad":
            os.system("start notepad")
            return "Opening Notepad."
        
        elif app_name == "calc":
            os.system("start calc")
            return "Opening Calculator."
        
        else:
            # Try generic system command
            os.system(f'start "{app_name}"')
            return f"Opening {app_name}."
    
    except Exception as e:
        return f"Failed to open application: {str(e)}"


def shutdown_pc():
    """Shutdown the computer."""
    try:
        os.system("shutdown /s /t 10")
        return "Shutting down the computer in 10 seconds."
    except Exception as e:
        return f"Failed to shutdown: {str(e)}"


def search_youtube(query):
    """Search YouTube."""
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}."
    except Exception as e:
        return f"Failed to search YouTube: {str(e)}"


def search_google(query):
    """Search Google."""
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching Google for {query}."
    except Exception as e:
        return f"Failed to search Google: {str(e)}"


def create_file(filename, content):
    """Create a file with content."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {filename} created successfully."
    except Exception as e:
        return f"Failed to create file: {str(e)}"
