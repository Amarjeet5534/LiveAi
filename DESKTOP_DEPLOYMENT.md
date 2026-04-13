# LiveAI Desktop - Windows Deployment Guide

## Quick Start (Fastest)

### Option 1: Batch File (Recommended for Quick Deployment)
1. Double-click **`LiveAI.bat`** in the project folder
2. It will automatically:
   - Create virtual environment if needed
   - Install dependencies
   - Launch the app

### Option 2: Python Launcher
1. Double-click **`launcher.py`** 
2. App will set up and launch automatically

### Option 3: Manual Launch
```bash
cd E:\LiveAI
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python desktop.py
```

---

## Prerequisites
- Windows 7/10/11
- Python 3.9+ installed globally (for batch file to work)
  - Download from: https://www.python.org/downloads/
  - **Important**: Check "Add Python to PATH" during installation
- Microphone connected to computer
- Ollama running on localhost:11434

---

## Ollama Setup (Required)

1. Download Ollama: https://ollama.ai
2. Install and start Ollama
3. Pull Phi3 model:
   ```bash
   ollama pull phi3
   ```
4. Ollama will run on `http://localhost:11434`

---

## Starting the Application

### Daily Use
- Simply double-click **`LiveAI.bat`** to start
- First launch will take 2-3 min (installing deps)
- Subsequent launches take 10-15 seconds

### What Happens
1. ✅ Backend API starts on `localhost:8000`
2. ✅ Desktop app window opens
3. ✅ Login screen appears (admin / admin123)
4. ✅ Ready to use

---

## Troubleshooting

### "Python not found" error
- Install Python 3.9+ from https://python.org
- Make sure to check "Add Python to PATH"

### "ModuleNotFoundError" when launching
- Delete `.venv` folder
- Try again (will reinstall dependencies)

### Microphone not working
- Check Windows mic settings
- Try another recording device
- In `desktop.py`, change `RECORDING_DEVICE_INDEX = 18` to another number

### Backend not connecting
- Make sure Ollama is running
- Check `http://localhost:11434` is accessible
- Restart the app

### Port already in use
- Close other Python processes: 
  ```powershell
  Stop-Process -ProcessName python -Force
  ```

---

## Advanced: Creating Standalone EXE

For one-click deployment without Python installed:

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file EXE (slow, large file ~500MB)
pyinstaller --onefile --windowed --name LiveAI desktop.py

# Or one-folder bundle (faster, smaller)
pyinstaller --onedir --windowed --name LiveAI desktop.py

# Run from: dist\LiveAI\LiveAI.exe
```

Note: Building EXE takes 10-30 min due to bundling ML models. See `build_exe.spec` for configuration.

---

## File Structure

```
LiveAI/
├── LiveAI.bat              ← Double-click to start (EASIEST)
├── launcher.py             ← Python launcher alternative
├── desktop.py              ← Main desktop app
├── .venv/                  ← Virtual environment (created on first run)
├── requirements.txt        ← Dependencies
├── backend/
│   └── fastapi_app.py      ← Backend API
├── frontend/
│   └── index.html          ← Web dashboard (localhost:3000)
└── ...
```

---

## System Architecture

```
LiveAI Desktop App (PyQt6)
          ↓
FastAPI Backend (localhost:8000)
          ↓
    Ollama LLM (localhost:11434)
```

- **Desktop**: Voice input/chat UI
- **Backend**: AI routing, security, database
- **Ollama**: AI engine (Phi3 model)

---

## Features

✅ Voice input (microphone recording)  
✅ Real-time transcription (Whisper)  
✅ AI responses (Ollama)  
✅ Text-to-speech output  
✅ Command history  
✅ Authentication (JWT)  
✅ Local database (SQLite)  
✅ Multiple user support  

---

## Login Credentials

**Default Admin Account:**
- Username: `admin`
- Password: `admin123`

---

## Support

For issues or questions, check:
1. `DEPLOYMENT_GUIDE.md` - System architecture
2. `README.md` - Project overview
3. `QUICK_START.md` - Setup instructions

