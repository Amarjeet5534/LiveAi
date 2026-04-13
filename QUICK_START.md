# 🚀 LiveAI Assistant - Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Python 3.10+
- Ollama running (`ollama serve`)
- 2GB RAM minimum

### Step 1: Verify System
```bash
cd e:\LiveAI
venv\Scripts\activate
python verify_system.py
```
Expected output:
```
✅ Ollama is running
✅ Mic found: Microphone Array
✅ Ollama replied: OK
✅ All systems ready!
```

### Step 2: Start Backend API
```bash
cd backend
python fastapi_app.py
```
You should see:
```
INFO:     Application startup complete
```

### Step 3: Serve Frontend
In another terminal:
```bash
cd frontend
python -m http.server 3000
```

### Step 4: Open Browser
Visit: **http://localhost:3000**

### Step 5: Register & Login
1. Click "Register"
2. Create account: username, email, password
3. Click "Login"
4. You're in!

---

## Commands to Try

| Command | What it does |
|---------|------------|
| `open chrome` | Opens Chrome browser |
| `search weather` | Searches Google for weather |
| `click` | Clicks mouse at current position |
| `scroll down` | Scrolls page down |
| `type hello` | Types "hello" |
| `screenshot` | Takes & analyzes screenshot |
| `what is 2+2` | AI answers the question |
| `🎤 button` | Voice input (click mic) |

---

## Docker Deployment (1 Command)

```bash
cd e:\LiveAI
docker-compose up -d
```

Access: http://localhost:3000

Stop:
```bash
docker-compose down
```

---

## System Architecture

```
┌─────────────────────┐
│  User Interface     │
│  (Web Dashboard)    │
│  http:3000          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  FastAPI Backend    │
│  (REST API)         │
│  http:8000          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  Ollama LLM         │
│  (AI Brain)         │
│  http:11434         │
└─────────────────────┘
```

---

## Safety Rules

🔴 **Blocked:**
- `rm -rf`, `format`, `shutdown`
- `del /f /s`, `taskkill`
- Patterns: `sudo`, `>>`, `&&`, `;`

🟢 **Allowed:**
- `open` apps
- `search` web
- `click`, `scroll`
- `type` text
- `screenshot`

---

## API Examples

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "secure123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "secure123"
  }'
# Returns: {"token": "..."}
```

### Execute Command
```bash
curl -X POST http://localhost:8000/api/commands/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "open chrome",
    "voice": false,
    "token": "YOUR_TOKEN"
  }'
```

---

## File Structure

```
e:\LiveAI
├── backend/
│   ├── fastapi_app.py          ← Start this
│   └── requirements.txt
├── frontend/
│   └── index.html              ← Serve this on port 3000
├── main.py                     ← Voice CLI (optional)
├── Dockerfile
├── docker-compose.yml
├── README.md                   ← Full documentation
└── PROJECT_DOCUMENTATION.md    ← Architecture details
```

---

## Troubleshooting

### Backend won't start
```bash
# Make sure Ollama is running
ollama serve

# Check port 8000 is free
netstat -an | findstr :8000
```

### Mic not working
```bash
# Find your microphone ID
python find_microphone.py

# Update VOICE_DEVICE in .env
```

### Database error
```bash
# Reset database
del liveai.db
python backend/fastapi_app.py
```

### Frontend not loading
```bash
# Check frontend is being served
python -m http.server 3000 --directory frontend
```

---

## Environment Variables

Create `.env` file:
```
STRICT_MODE=True
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=phi3
VOICE_DEVICE=18
```

---

## Performance Checklist

- ✅ Ollama running? (Try: `curl http://localhost:11434/api/tags`)
- ✅ FastAPI running? (Try: `curl http://localhost:8000/api/health`)
- ✅ Frontend loaded? (Try: `http://localhost:3000`)
- ✅ Microphone detected? (Try: `python find_microphone.py`)
- ✅ Database created? (Check: `python verify_system.py`)

---

## Next Steps

1. **Customize Commands**: Edit `backend/fastapi_app.py` DANGEROUS_COMMANDS & ALLOWED_COMMANDS
2. **Deploy to Cloud**: Use Docker image on AWS/Azure/GCP
3. **Add More Models**: Change LLM_MODEL in .env
4. **Mobile App**: Deploy frontend as PWA
5. **Enterprise**: Add PostgreSQL, Redis, monitoring

---

## Support

- 📖 Full README: see `README.md`
- 📋 Architecture: see `PROJECT_DOCUMENTATION.md`
- 🤔 Issues: Check logs in `liveai.log`
- 🐳 Docker help: `docker-compose logs -f api`

---

**Status**: ✅ Ready to Deploy  
**Version**: 1.0 Production

**Enjoy your AI Assistant!** 🎉
