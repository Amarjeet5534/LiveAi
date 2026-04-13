import json
import re

def decide_tool(user_input):
    """Fast keyword-based tool detection (no API calls)."""
    text = user_input.lower().strip()
    
    print(f"[DEBUG] Analyzing: {text}")
    
    # OPEN APP - Priority 1
    open_keywords = ["open", "launch", "start", "run"]
    app_keywords = ["chrome", "code", "notepad", "calculator", "calc", "vscode", "vs code", "google", "edge"]
    
    if any(kw in text for kw in open_keywords):
        for app in app_keywords:
            if app in text:
                app_name = app.replace("vs code", "code").replace("vscode", "code")
                print(f"[DEBUG] Detected: open_app({app_name})")
                return {"tool": "open_app", "arguments": {"app_name": app_name}}
    
    # SHUTDOWN - Priority 2
    shutdown_keywords = ["shutdown", "turn off", "power off", "restart", "reboot", "close computer"]
    if any(kw in text for kw in shutdown_keywords):
        print(f"[DEBUG] Detected: shutdown_pc()")
        return {"tool": "shutdown_pc", "arguments": {}}
    
    # YOUTUBE SEARCH - Priority 3
    youtube_keywords = ["youtube", "search youtube", "youtube search"]
    if any(kw in text for kw in youtube_keywords):
        # Extract query after keyword
        for kw in youtube_keywords:
            if kw in text:
                query = text.replace(kw, "").strip()
                if query:
                    print(f"[DEBUG] Detected: search_youtube({query})")
                    return {"tool": "search_youtube", "arguments": {"query": query}}
    
    # GOOGLE SEARCH - Priority 4
    google_keywords = ["google", "search google", "search for", "look up"]
    if any(kw in text for kw in google_keywords):
        # Extract query
        for kw in google_keywords:
            if kw in text:
                query = text.replace(kw, "").strip()
                if query and len(query) > 2:
                    print(f"[DEBUG] Detected: search_google({query})")
                    return {"tool": "search_google", "arguments": {"query": query}}
    
    # CREATE FILE - Priority 5
    file_keywords = ["create file", "create a file", "save file", "write file"]
    if any(kw in text for kw in file_keywords):
        print(f"[DEBUG] Detected: create_file()")
        return {"tool": "create_file", "arguments": {"filename": "note.txt", "content": text}}
    
    # No tool detected
    print(f"[DEBUG] No tool detected - will use AI response")
    return None
