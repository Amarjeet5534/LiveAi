# Live AI Assistant - Complete Deployment Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Live AI Assistant                       │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
           DESKTOP APP   WEB APP    DATABASE
         (PyQt6 GUI)  (HTML/JS)   (SQLite Local)
                │           │           │
                └───────────┼───────────┘
                            │
                            ▼
                    FastAPI Backend
                  (Python, localhost:8000)
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
            Ollama      Whisper      Edge-TTS
         (LLM Response)  (Voice)     (Audio Out)
```

## Components

### 1. Desktop App (PyQt6)
- **File**: `desktop.py`
- **Type**: Native Windows/Mac/Linux application
- **Features**:
  - Voice recording (5 seconds, real-time transcription)
  - Chat interface with message history
  - Quick command buttons (Open Chrome, Weather, Screenshot, Take Photo)
  - Authentication (login/register)
  - Command history sidebar
  - Session statistics
  - Local database integration

### 2. Web App (HTML/JavaScript)
- **File**: `frontend/index.html`
- **Type**: Browser-based dashboard
- **Features**:
  - Web Speech API for voice input
  - Chat interface
  - Real-time message updates
  - LocalStorage for session persistence
  - Responsive design (desktop & mobile)

### 3. Backend API (FastAPI)
- **File**: `backend/fastapi_app.py`
- **Type**: REST API server
- **Features**:
  - User authentication (JWT tokens)
  - Command execution with safety validation
  - Command history tracking
  - Multi-user support
  - Audit logging
  - SQLite database

### 4. Database (SQLite - Local)
- **Location**: `data/app.db`
- **Tables**:
  - `users` - User accounts and credentials
  - `sessions` - Active sessions and tokens
  - `command_history` - All executed commands
  - `audit_log` - Security and activity logs

---

## Installation Steps

### Prerequisites
- Python 3.9+
- Ollama running locally on `localhost:11434`
- Microphone connected to computer
- 4GB RAM minimum

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd e:\LiveAI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# Install all dependencies (web + desktop + backend)
pip install -r requirements.txt
```

### Step 2: Configure Backend

Create `.env` file in project root:
```env
# Database
DATABASE_URL=sqlite:///./data/app.db

# Ollama
OLLAMA_HOST=http://localhost:11434

# Voice
RECORDING_DEVICE_INDEX=18

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False

# Security
SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Step 3: Start Backend API

```bash
# Option A: Direct Python
python backend/fastapi_app.py

# Option B: Using Uvicorn
uvicorn backend.fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

---

## Usage Options

### Option A: Desktop Application

Perfect for: Power users, voice-first workflow, native app experience

**Steps:**
1. Terminal 1: Start Backend API (as above)
2. Terminal 2: Run Desktop App
   ```bash
   python desktop.py
   ```
3. Desktop window opens → Login/Register
4. Click "🎤 Record Voice" or type commands
5. View history and statistics in sidebar

**Screenshots Command Flow:**
```
User: "Open Chrome" (voice)
     ↓
Desktop App Records 5 seconds
     ↓
Whisper Transcribes: "Open Chrome"
     ↓
Send to Backend API
     ↓
Backend Validates (safety check)
     ↓
Execute OS command
     ↓
Chat shows: "Opening Chrome..."
     ↓
Chrome launches on your desktop
```

### Option B: Web Application

Perfect for: Remote access, team collaboration, browser-based workflow

**Steps:**
1. Terminal 1: Start Backend API
   ```bash
   python backend/fastapi_app.py
   ```
2. Terminal 2: Start Web Server
   ```bash
   python -m http.server 3000 --directory frontend
   ```
3. Open Browser: `http://localhost:3000`
4. Create account or login
5. Use microphone icon or type commands
6. See command history on left sidebar

**Features:**
- Real-time chat with backend
- Web Speech API for voice input (browser native)
- Responsive on mobile
- Session persistence with localStorage

### Option C: Docker Deployment (Advanced)

Perfect for: Production deployment, reproducible environment

```bash
# Build and run all services
docker-compose up --build

# Services available at:
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Ollama: http://localhost:11434
```

---

## Database

### Schema

**users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**command_history Table**
```sql
CREATE TABLE command_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    command VARCHAR(255) NOT NULL,
    result TEXT,
    status VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### Accessing Database

```bash
# View data with SQLite CLI
sqlite3 data/app.db

# Example queries:
.tables
SELECT * FROM users;
SELECT command, result FROM command_history LIMIT 10;
```

---

## Features Across All Platforms

### ✅ Voice Commands
- **Desktop**: Microphone → Whisper → Ollama → Execute
- **Web**: Web Speech API → Backend Transcription → Ollama → Execute
- **Latency**: 2-3 seconds total (local processing only)

### ✅ Safety Validation
- Blocks dangerous commands: `rm -rf`, `shutdown`, `sudo`
- Whitelist-based execution for system commands
- Audit logging for all actions
- Multi-user isolation

### ✅ Natural Language Processing
- Ollama Phi3 model (local, no API calls needed)
- Fast keyword detection for quick responses
- Context-aware responses
- 15-word response limit for TTS speed

### ✅ Text-to-Speech
- Edge TTS (high-quality, English)
- Automatic audio playback
- Error handling for network issues
- Works offline (backend hosted locally)

### ✅ Authentication & Multi-User
- JWT tokens for session management
- Per-user command history
- Secure password hashing (bcrypt)
- Session timeout (24 hours default)

### ✅ Command History
- All commands logged to database
- Searchable command history
- Performance statistics
- Audit trail for compliance

### ✅ Quick Commands
- Open Chrome
- Check Weather
- Take Screenshot
- Search Web
- File Operations
- Customizable command list

---

## Common Commands to Try

```
"Open Chrome"                    → Launches Chrome browser
"What is the weather?"          → Shows weather information
"Search for Python tutorials"   → Searches DuckDuckGo
"Take a screenshot"             → Saves screenshot to desktop
"Open notepad"                  → Launches text editor
"Scroll down"                   → Simulates scroll down
"Click"                         → Simulates mouse click
"What's the current time?"      → Tells current time
"Tell me a joke"                → AI generates joke
```

---

## Troubleshooting

### Issue: Desktop app won't start
```
Solution: 
1. Verify PyQt6 installed: pip install PyQt6
2. Check Python 3.9+: python --version
3. Ensure backend API running first
```

### Issue: Microphone not detected
```
Solution:
1. Check device index in config: device 18 might not be correct
2. List available devices: python verify_system.py
3. Update RECORDING_DEVICE_INDEX in .env or code
```

### Issue: Voice commands not working
```
Solution:
1. Verify Ollama running: curl http://localhost:11434/api/tags
2. Check Whisper model installed
3. Test directly: python -c "import whisper; print('OK')"
4. Check microphone levels in Windows settings
```

### Issue: Web app not loading
```
Solution:
1. Start web server: python -m http.server 3000 --directory frontend
2. Open http://localhost:3000 (not file://)
3. Check browser console for errors (F12)
4. Ensure backend API running on port 8000
```

### Issue: Database locked error
```
Solution:
1. Close all Python processes: taskkill /IM python.exe
2. Delete data/app.db and restart (will recreate)
3. Check for multiple API instances running
```

---

## Performance Tips

1. **Faster Response Time**:
   - Keep Ollama model in memory (warm start)
   - Use quantized Whisper model (int8)
   - Set response max_length to 15 words

2. **Lower Microphone Noise**:
   - Use noise-cancelling headset
   - Record in quiet environment
   - Adjust microphone input level in Windows

3. **Better Accuracy**:
   - Speak clearly and naturally
   - Use full sentences (not single words)
   - Wait 2 seconds after command before releasing microphone

---

## What's Next?

### Phase 2 Features (Coming Soon)
- Mobile app (React Native)
- Advanced analytics dashboard
- Custom command builder
- Voice profile training
- Multi-language support
- Web API documentation (Swagger UI)

### Phase 3: Advanced
- Integrate with smart home (Home Assistant)
- Calendar integration
- Email automation
- Custom Ollama models
- Cloud sync option

---

## File Structure

```
e:\LiveAI\
├── desktop.py                 # Desktop PyQt6 app
├── main.py                    # Legacy CLI voice interface
├── requirements.txt           # All dependencies
├── backend/
│   ├── fastapi_app.py        # REST API server (600+ lines)
│   ├── config.py             # Configuration
│   └── requirements.txt       # Backend dependencies
├── frontend/
│   └── index.html            # Web dashboard (400+ lines)
├── data/
│   ├── app.db                # SQLite database
│   ├── audio/                # Audio files
│   └── memory/               # Vector DB
├── voice/
│   ├── speech_to_text.py
│   └── text_to_speech.py
├── agent/
│   ├── controller.py
│   ├── local_llm.py
│   └── tools.py
├── docker-compose.yml         # Multi-container orchestration
├── Dockerfile                # Container image
├── nginx.conf                # Web server config
└── README.md                 # Project documentation
```

---

## Support & Documentation

- **API Docs**: Start backend, then visit `http://localhost:8000/docs`
- **Database**: Check `data/app.db` with SQLite Browser
- **Logs**: Check console output for errors
- **Issues**: Check `.env` file and permissions

---

**Happy voice commanding! 🎙️**
