"""
Configuration for LiveAI Backend
Environment variables and settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///liveai.db")
DB_FILE = os.getenv("DB_FILE", "liveai.db")

# Ollama / LLM
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "phi3")

# Voice
VOICE_DEVICE = int(os.getenv("VOICE_DEVICE", 18))
RECORDING_DURATION = int(os.getenv("RECORDING_DURATION", 5))

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", 24))

# Upload
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "liveai.log")

# Features
ENABLE_VOICE = os.getenv("ENABLE_VOICE", "True").lower() == "true"
ENABLE_FILE_UPLOAD = os.getenv("ENABLE_FILE_UPLOAD", "False").lower() == "true"
ENABLE_ADMIN_PANEL = os.getenv("ENABLE_ADMIN_PANEL", "True").lower() == "true"

# Safety
STRICT_MODE = os.getenv("STRICT_MODE", "True").lower() == "true"

print("✅ Configuration loaded")
