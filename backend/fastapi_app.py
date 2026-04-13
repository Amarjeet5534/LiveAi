"""
FastAPI Backend for LiveAI Assistant
Production-ready API with authentication, safety, and logging
"""

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import hashlib
import secrets
import json
import os
from typing import Optional, List
import logging
import requests

# ============================================
# CONFIGURATION
# ============================================
app = FastAPI(
    title="LiveAI Assistant",
    description="Industry-ready AI assistant with voice, web, and mobile support",
    version="1.0.0"
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database path
DB_FILE = "liveai.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Ollama configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "phi3"

# ============================================
# REAL-TIME DATA INTEGRATION
# ============================================
def get_weather(location: str = "current") -> str:
    """Get real-time weather information"""
    try:
        # Using wttr.in API (free, no key needed)
        response = requests.get(
            f"https://wttr.in/{location}?format=j1",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            temp = current['temp_C']
            condition = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            wind = current['windspeedKmph']
            return f"Weather: {temp}°C, {condition}. Humidity: {humidity}%. Wind: {wind} km/h"
        else:
            # Fallback to wttr.in plain text
            response = requests.get(f"https://wttr.in/{location}?format=3", timeout=10)
            return response.text.strip()
    except Exception as e:
        logger.warning(f"Weather error: {str(e)}")
        return f"I cannot fetch weather right now. Try asking about weather in a specific city like 'what is the weather in London'"

def web_search(query: str) -> str:
    """Search the web for information"""
    try:
        # Try multiple search methods for reliability
        
        # Method 1: Try DuckDuckGo
        try:
            response = requests.get(
                f"https://api.duckduckgo.com/",
                params={"q": query, "format": "json"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('AbstractText'):
                    return data['AbstractText'][:150]
                elif data.get('RelatedTopics') and len(data['RelatedTopics']) > 0:
                    first_result = data['RelatedTopics'][0]
                    if 'Text' in first_result:
                        return first_result['Text'][:150]
        except:
            pass
        
        # Method 2: Try Wikipedia search (more reliable)
        try:
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json"
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                results = data.get('query', {}).get('search', [])
                if results:
                    # Extract snippet from first result
                    snippet = results[0].get('snippet', '')
                    # Clean HTML tags
                    import re
                    snippet = re.sub('<[^<]+?>', '', snippet)
                    return snippet[:150]
        except:
            pass
        
        # Method 3: Use Ollama to answer the question if search fails
        return get_ollama_response(query)
        
    except Exception as e:
        logger.warning(f"Search error: {str(e)}")
        return f"Cannot search right now for: {query}"

# ============================================
# OLLAMA INTEGRATION
# ============================================
def get_ollama_response(prompt: str) -> str:
    """Get response from Ollama AI model"""
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=60  # Increased: Ollama may need time to generate
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "").strip()
            # Limit response to 25 words
            words = answer.split()[:25]
            return " ".join(words)
        else:
            return "I'm having trouble thinking right now"
    except Exception as e:
        logger.warning(f"Ollama error: {str(e)}")
        return "Sorry, I couldn't get a response from the AI"

# ============================================
# SAFETY RULES - CRITICAL
# ============================================
DANGEROUS_COMMANDS = [
    "rm -rf",
    "format",
    "del /f /s",
    "shutdown",
    "restart",
    "taskkill",
    "pkill",
    ":ForceDelete",
    "cipher /w:",
    "diskpart"
]

ALLOWED_COMMANDS = [
    "open chrome",
    "open code",
    "search",
    "click",
    "scroll",
    "type",
    "screenshot",
    "read file",
    "create file",
    "list files",
]

# ============================================
# DATA MODELS
# ============================================
class User(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class CommandRequest(BaseModel):
    command: str
    voice: bool = False

class CommandResponse(BaseModel):
    success: bool
    response: str
    command_id: str
    timestamp: str

class CommandHistory(BaseModel):
    id: str
    user: str
    command: str
    response: str
    timestamp: str
    status: str

# ============================================
# DATABASE SETUP
# ============================================
def init_db():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )''')
    
    # Command history table
    c.execute('''CREATE TABLE IF NOT EXISTS command_history (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        command TEXT NOT NULL,
        response TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id TEXT,
        expires_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Audit log table
    c.execute('''CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        action TEXT,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

# ============================================
# AUTHENTICATION
# ============================================
def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"

def verify_password(password: str, hash_: str) -> bool:
    """Verify password against hash"""
    try:
        salt, pwd_hash = hash_.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == pwd_hash
    except:
        return False

def create_session(user_id: str) -> str:
    """Create session token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=7)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
              (token, user_id, expires_at))
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Session created for user {user_id}")
    return token

def verify_session(token: str) -> Optional[str]:
    """Verify session token and return user_id"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT user_id FROM sessions WHERE token = ? AND expires_at > datetime('now')",
              (token,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# ============================================
# COMMAND SAFETY
# ============================================
def is_command_safe(command: str) -> tuple[bool, str]:
    """Check if command is safe to execute"""
    command_lower = command.lower().strip()
    
    # Check blocklist
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous.lower() in command_lower:
            return False, f"❌ Dangerous command blocked: {dangerous}"
    
    # Check if contains suspicious patterns
    suspicious = ["sudo", ">>", "|", "&&", ";"]
    for pattern in suspicious:
        if pattern in command_lower:
            return False, f"❌ Suspicious pattern detected: {pattern}"
    
    return True, "✅ Command is safe"

# ============================================
# API ENDPOINTS - AUTHENTICATION
# ============================================
@app.post("/api/auth/register")
async def register(user: User):
    """Register new user"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        user_id = secrets.token_urlsafe(16)
        pwd_hash = hash_password(user.password)
        
        c.execute("""INSERT INTO users (id, username, email, password_hash) 
                     VALUES (?, ?, ?, ?)""",
                  (user_id, user.username, user.email, pwd_hash))
        conn.commit()
        
        logger.info(f"✅ User registered: {user.username}")
        return {"success": True, "user_id": user_id, "message": "Registration successful"}
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    finally:
        conn.close()

@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    """User login"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute("SELECT id, password_hash, is_active FROM users WHERE username = ?",
              (credentials.username,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id, pwd_hash, is_active = result
    
    if not is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")
    
    if not verify_password(credentials.password, pwd_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_session(user_id)
    logger.info(f"✅ User logged in: {credentials.username}")
    
    return {"success": True, "token": token, "user_id": user_id}

# ============================================
# API ENDPOINTS - COMMANDS
# ============================================
@app.post("/api/commands/execute")
async def execute_command(request: CommandRequest, authorization: str = Header(None)):
    """Execute command with safety checks and real capabilities"""
    
    # Extract token from Authorization header
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    
    # Verify session
    user_id = verify_session(token) if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Safety check
    is_safe, safety_msg = is_command_safe(request.command)
    if not is_safe:
        logger.warning(f"❌ Blocked command from {user_id}: {request.command}")
        return CommandResponse(
            success=False,
            response=safety_msg,
            command_id="",
            timestamp=datetime.now().isoformat()
        )
    
    # Get response from appropriate source
    command_id = secrets.token_urlsafe(16)
    command_lower = request.command.lower()
    
    # Route to appropriate tool based on user's command
    if "weather" in command_lower or "temperature" in command_lower:
        # Extract location if provided
        location = "current"
        if " in " in command_lower:
            location = request.command.split(" in ", 1)[1].strip()
        elif " at " in command_lower:
            location = request.command.split(" at ", 1)[1].strip()
        ai_response = get_weather(location)
    elif any(keyword in command_lower for keyword in ["search", "find", "what is", "who is", "how", "when", "where"]):
        # Use web search for general knowledge questions
        ai_response = web_search(request.command)
    else:
        # Use Ollama for everything else
        ai_response = get_ollama_response(request.command)
    
    # Log command
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO command_history (id, user_id, command, response, status)
                 VALUES (?, ?, ?, ?, ?)""",
              (command_id, user_id, request.command, ai_response, "completed"))
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Command executed: {request.command}")
    
    return CommandResponse(
        success=True,
        response=ai_response,
        command_id=command_id,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/commands/history")
async def get_command_history(token: str = None, limit: int = 50):
    """Get user's command history"""
    user_id = verify_session(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""SELECT id, command, response, status, created_at 
                 FROM command_history 
                 WHERE user_id = ? 
                 ORDER BY created_at DESC 
                 LIMIT ?""",
              (user_id, limit))
    results = c.fetchall()
    conn.close()
    
    history = [CommandHistory(
        id=r[0],
        user=user_id,
        command=r[1],
        response=r[2] or "",
        timestamp=r[4],
        status=r[3]
    ) for r in results]
    
    return {"success": True, "history": history}

# ============================================
# API ENDPOINTS - TRANSCRIPTION
# ============================================
@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio file to text using faster-whisper with fallbacks"""
    import uuid
    temp_path = None
    
    try:
        # Read audio file
        contents = await file.read()
        
        if not contents:
            return {"text": "", "error": "Empty audio file"}
        
        # Save temporarily with unique name to avoid file lock conflicts
        temp_dir = Path("uploads")
        temp_dir.mkdir(exist_ok=True)
        unique_name = f"audio_{uuid.uuid4().hex[:8]}.wav"
        temp_path = temp_dir / unique_name
        
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        file_size = len(contents)
        logger.info(f"📁 Audio file size: {file_size} bytes")
        
        # Check file validity
        if file_size < 4000:  # Less than ~0.25 seconds at 16kHz stereo
            return {"text": "", "error": "Audio file too short - record for at least 1 second"}
        
        try:
            # Load and validate audio
            import librosa
            import numpy as np
            
            logger.info("🔍 Loading audio for validation...")
            y, sr = librosa.load(str(temp_path), sr=16000, mono=True)
            logger.info(f"✓ Loaded: {len(y)} samples at {sr}Hz")
            
            # Check audio duration
            duration = len(y) / sr
            logger.info(f"⏱️ Duration: {duration:.2f} seconds")
            
            if duration < 0.5:
                return {"text": "", "error": "Audio too short - speak for at least 1 second"}
            
            # Check signal level
            rms_val = float(np.sqrt(np.mean(y**2)))
            logger.info(f"📊 RMS level: {rms_val:.6f}")
            
            if rms_val < 0.001:
                return {"text": "", "error": "Audio is too quiet - speak louder into the microphone"}
            
            logger.info("✓ Audio validation passed")
            
        except Exception as e:
            logger.warning(f"⚠️ Audio validation warning: {str(e)}")
        
        try:
            # Try faster-whisper with multiple attempts
            from faster_whisper import WhisperModel
            
            logger.info("🎙️ Attempting speech-to-text transcription (English)...")
            model = WhisperModel("base", device="cpu", compute_type="int8")
            
            # First attempt: English-only, NO VAD (VAD too aggressive)
            segments, info = model.transcribe(
                str(temp_path), 
                language="en",  # Force English
                beam_size=3,
                best_of=3,
                temperature=0.0,
                vad_filter=False  # Disable VAD - it's too aggressive and removes speech
            )
            
            text = " ".join([segment.text.strip() for segment in segments if segment.text.strip()]).strip()
            
            if text:
                logger.info(f"✅ Transcribed successfully: {text[:80]}...")
                return {"text": text}
            else:
                logger.warning("⚠️ No text extracted from clean audio")
        
        except Exception as e:
            logger.error(f"❌ Faster-whisper failed: {str(e)}")
        
        # Final fallback - try with different temperature settings
        try:
            logger.info("🔄 Trying fallback with temperature sweep...")
            from faster_whisper import WhisperModel
            model = WhisperModel("base", device="cpu", compute_type="int8")
            
            # Try with temperature sweep for robustness
            for temp in [0.1, 0.3, 0.5]:
                segments, info = model.transcribe(
                    str(temp_path),
                    language="en",
                    beam_size=2,
                    temperature=temp,
                    vad_filter=False
                )
                
                text = " ".join([segment.text.strip() for segment in segments if segment.text.strip()]).strip()
                
                if text:
                    logger.info(f"✅ Transcribed (temp={temp}): {text[:80]}...")
                    return {"text": text}
        
        except Exception as e:
            logger.error(f"❌ Fallback also failed: {str(e)}")
        
        logger.error("❌ Could not extract any speech from audio")
        return {"text": "", "error": "Could not understand speech - try speaking much louder and more clearly, or get closer to the microphone"}
        
    except Exception as e:
        logger.error(f"❌ Transcription error: {str(e)}")
        return {"text": "", "error": f"Transcription service error: {str(e)[:50]}"}
    
    finally:
        # Always clean up temp file
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete temp file {temp_path}: {e}")

# ============================================
# STARTUP
# ============================================
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("🚀 LiveAI Backend Started")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
