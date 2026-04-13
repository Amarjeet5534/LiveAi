# Desktop + Web + Database - Quick Start (5 Minutes)

## What You're Getting

| Component | Type | Launch | Access |
|-----------|------|--------|--------|
| **Desktop App** | Native PyQt6 window | `python desktop.py` | Taskbar/Window |
| **Web Dashboard** | Browser interface | `python -m http.server 3000 --directory frontend` | http://localhost:3000 |
| **Database** | SQLite (local file) | Automatic | `data/app.db` |
| **Backend API** | REST server | `python backend/fastapi_app.py` | http://localhost:8000 |
| **Voice Engine** | Ollama + Whisper | Pre-running | localhost:11434 |

---

## Before You Start

✅ Check these boxes:
- [ ] Ollama running (`http://localhost:11434/api/tags` should return model list)
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Microphone connected and working
- [ ] In project folder: `e:\LiveAI`

---

## Start Everything (3 Terminals)

### Terminal 1: Backend API
```bash
cd e:\LiveAI
venv\Scripts\activate
python backend/fastapi_app.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

### Terminal 2: Desktop App (Recommended for Voice)

```bash
cd e:\LiveAI
venv\Scripts\activate
python desktop.py
```

**What happens:**
- Window opens → Login screen
- Create account (username/password) or use existing
- Main chat window with microphone button
- Click "🎤 Record Voice" to command
- Type commands in textbox
- See results in chat

**Try these commands:**
```
"Open Chrome"
"What is the weather"
"Take screenshot"
"Tell me a joke"
```

---

### Terminal 3: Web Dashboard (Optional, for Browser)

```bash
cd e:\LiveAI
venv\Scripts\activate
python -m http.server 3000 --directory frontend
```

**What happens:**
- Open browser to: `http://localhost:3000`
- Login with same account as desktop
- Use same interface but in browser
- Works on phone/tablet too (same WiFi)

---

## Use Cases

### 🖥️ Power User (Desktop App)
```
1. Start Terminal 1 (Backend API)
2. Start Terminal 2 (Desktop App)
3. Desktop window opens
4. Click microphone button → speak → see result
5. Fast voice-first workflow
```

### 🌐 Team User (Web Dashboard)  
```
1. Start Terminal 1 (Backend API)
2. Start Terminal 3 (Web Server)
3. Open http://localhost:3000 in browser
4. Click microphone or type
5. Share URL with teammates on same network
```

### 🔄 Full System (All 3)
```
1. Start Terminal 1 (Backend)
2. Start Terminal 2 (Desktop)
3. Start Terminal 3 (Web)
4. Use both desktop and web simultaneously
5. Same database, same user account
```

---

## Database Auto-Setup

When you first run the backend, it automatically:
- ✅ Creates `data/app.db` 
- ✅ Creates all tables: users, command_history, sessions, audit_log
- ✅ Ready to store user data immediately

**View database content:**
```bash
sqlite3 data/app.db
.tables
SELECT * FROM command_history LIMIT 5;
.quit
```

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port 8000 already in use** | `netstat -ano \| findstr :8000` then close app |
| **Desktop app crashes on start** | Run `pip install PyQt6` |
| **Microphone not found** | Run `python verify_system.py` to check device |
| **Web page blank** | Check Terminal 1 API is running |
| **"Command not found" errors** | Backend not running - start Terminal 1 |

---

## Key Files

- **Desktop GUI**: `desktop.py` (500 lines)
- **API Server**: `backend/fastapi_app.py` (600 lines)
- **Web UI**: `frontend/index.html` (400 lines)
- **Database**: `data/app.db` (auto-created)
- **Config**: `.env` (create if needed)

---

## Common Commands to Test

```
"Open Chrome"                   → Chrome launches
"What's the weather"            → Gets weather
"Search for Python"             → Searches web
"Take screenshot"               → Saves screenshot
"Tell me a joke"                → AI responds
"What time is it"               → Reads current time
"Click the mouse"               → Clicks at cursor
"Scroll down"                   → Scrolls window
```

---

## Advanced: Using All 3 Simultaneously

You can run **desktop + web at the same time** with same backend:

Terminal arrangement:
```
Terminal 1 (Backend)  │ Terminal 2 (Desktop) │ Terminal 3 (Web)
python backend/...    │ python desktop.py    │ python -m http.server
[API Running]         │ [App Window]         │ [http://localhost:3000]
                      │ Login → Use voice    │ Login → Use browser
```

Both apps use **same database** → shared history!

---

## Stop Everything

Press `Ctrl+C` in each terminal to stop:
1. Terminal 1 (Backend) - Ctrl+C
2. Terminal 2 (Desktop) - Ctrl+C or close window  
3. Terminal 3 (Web server) - Ctrl+C

Database (`data/app.db`) stays intact for next run.

---

## What's Different from Main.py?

| Feature | Main.py | Desktop App | Web App |
|---------|---------|-------------|---------|
| Interface | CLI text | GUI window | Browser |
| User Auth | None | Login/register | Login/register |
| History View | Limited | Full sidebar | Full sidebar |
| Multi-user | No | Yes | Yes |
| Database | Text file | SQLite | SQLite |
| Deployment | CLI only | Desktop exe | Any browser |

---

## Next: Configure Safety Rules

Edit `backend/fastapi_app.py` line ~50:

```python
DANGEROUS_COMMANDS = [
    "rm -rf",
    "shutdown",
    "reboot",
    # Add your blocked commands here
]

ALLOWED_COMMANDS = {
    "open chrome": "start chrome",
    "open firefox": "start firefox",
    # Add safe shortcuts here
}
```

Then restart backend API.

---

**🎉 You now have:**
- ✅ Desktop App
- ✅ Web Dashboard  
- ✅ Local SQLite Database
- ✅ All in 5 minutes!
