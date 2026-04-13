# 🤖 LiveAI Assistant - Industry Ready

An intelligent AI assistant that can perform tasks on your computer via voice, web, or mobile app. Built with FastAPI, Ollama LLM, and modern web technologies.

## ✨ Features

✅ **Voice Interface** - Talk to control your computer  
✅ **Web Dashboard** - Beautiful, responsive interface  
✅ **User Management** - Multi-user with authentication  
✅ **Command History** - Track all executed commands  
✅ **Safety First** - Blocks dangerous/critical operations  
✅ **Admin Panel** - Manage users and monitor activity  
✅ **Local LLM** - Uses Ollama (Phi3 model)  
✅ **Production Ready** - Logging, error handling, security  

## 🏗️ Architecture

```
LiveAI Assistant
├── Backend (FastAPI)
│   ├── Authentication (JWT Sessions)
│   ├── Command Execution (with safety checks)
│   ├── Voice Processing (Ollama + Whisper)
│   ├── Database (SQLite)
│   └── Logging & Audit
├── Frontend (Web Dashboard)
│   ├── Chat Interface
│   ├── Voice Input
│   ├── Command History
│   └── Admin Panel
└── Deployment
    ├── Docker Containerization
    └── Docker Compose (Multi-container)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Ollama (running on localhost:11434)
- Git

### 1. Clone & Setup

```bash
cd e:\LiveAI
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
```

### 2. Environment Configuration

Create `.env` file:

```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Ollama
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=phi3

# Voice
VOICE_DEVICE=18
RECORDING_DURATION=5

# Security
SECRET_KEY=your-super-secret-key-change-this
STRICT_MODE=True

# Features
ENABLE_VOICE=True
ENABLE_FILE_UPLOAD=False
ENABLE_ADMIN_PANEL=True
```

### 3. Start Services

**Terminal 1 - Ollama (if not already running):**
```bash
ollama serve
```

**Terminal 2 - Backend API:**
```bash
cd backend
venv\Scripts\activate
python fastapi_app.py
# or
uvicorn fastapi_app:app --reload --port 8000
```

**Terminal 3 - Frontend (Simple HTTP Server):**
```bash
# Python
python -m http.server 3000 --directory frontend

# Or using Node.js
npx http-server frontend -p 3000
```

### 4. Access the App

- **Web Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin.html (coming soon)

## 📱 API Endpoints

### Authentication

```bash
# Register
POST /api/auth/register
{
  "username": "john",
  "email": "john@example.com",
  "password": "secure123"
}

# Login
POST /api/auth/login
{
  "username": "john",
  "password": "secure123"
}
→ Returns: { "token": "...", "user_id": "..." }
```

### Commands

```bash
# Execute Command
POST /api/commands/execute
Headers: Authorization: Bearer {token}
{
  "command": "open chrome",
  "voice": false
}

# Get History
GET /api/commands/history?limit=50&token={token}
→ Returns: { "history": [...] }
```

### Health Check

```bash
GET /api/health
```

## 🔒 Safety & Security

### Blocked Commands
- `rm -rf`, `format`, `del /f /s`
- `shutdown`, `restart`, `taskkill`
- Any command with: `sudo`, `>>`, `&&`, `;`

### Allowed Keywords
- `open` (applications)
- `search` (web search)
- `click`, `scroll` (mouse control)
- `type` (keyboard input)
- `screenshot` (screen capture)
- `read file`, `create file` (safe file ops)

Enable/disable in `backend/fastapi_app.py`

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t liveai:latest .
```

### Run Container

```bash
docker run -p 8000:8000 -p 3000:3000 \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  liveai:latest
```

### Docker Compose (Multi-container)

```bash
# Includes: FastAPI, Frontend, Ollama
docker-compose up -d
```

Access: http://localhost:3000

## 📊 Database Schema

### Users Table
```sql
- id (PRIMARY KEY)
- username (UNIQUE)
- email (UNIQUE)
- password_hash
- role (user/admin)
- created_at
- is_active
```

### Command History
```sql
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- command
- response
- status (pending/success/error)
- created_at
```

### Sessions
```sql
- token (PRIMARY KEY)
- user_id (FOREIGN KEY)
- expires_at
```

### Audit Log
```sql
- id (AUTO INCREMENT)
- user_id
- action
- details
- ip_address
- created_at
```

## 🎯 Command Examples

### Voice Commands
```
"Open chrome"
"Search weather"
"Click"
"Scroll down"
"Type hello"
"Take screenshot"
"What's on screen"
"Read C:\file.txt"
```

### Web Dashboard
Type in the text input or use quick command buttons

### API via cURL
```bash
curl -X POST http://localhost:8000/api/commands/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "open chrome",
    "voice": false,
    "token": "YOUR_TOKEN"
  }'
```

## 📈 Monitoring & Logging

Logs are saved to: `liveai.log`

View logs:
```bash
tail -f liveai.log
```

Check database:
```bash
sqlite3 liveai.db ".tables"
sqlite3 liveai.db "SELECT * FROM command_history LIMIT 10;"
```

## 🔧 Configuration Options

| Variable | Default | Purpose |
|----------|---------|---------|
| `STRICT_MODE` | True | Block dangerous commands |
| `ENABLE_VOICE` | True | Allow voice input |
| `ENABLE_FILE_UPLOAD` | False | Allow file uploads |
| `VOICE_DEVICE` | 18 | Microphone device ID |
| `LLM_MODEL` | phi3 | Ollama model name |
| `SESSION_TIMEOUT_HOURS` | 24 | Session expiry |

## 🎓 Next Steps & Enhancements

### Phase 2 - Add These Features
- [ ] Admin Dashboard UI (manage users, monitor activity)
- [ ] API Key authentication (for integrations)
- [ ] Rate limiting (prevent abuse)
- [ ] WebSocket support (real-time updates)
- [ ] Advanced analytics dashboards
- [ ] Multi-language support
- [ ] Cloud storage integration

### Phase 3 - Mobile Apps
- [ ] React Native / Flutter mobile app
- [ ] Offline mode support
- [ ] Push notifications
- [ ] Advanced voice processing

### Phase 4 - Enterprise
- [ ] LDAP/Active Directory integration
- [ ] RBAC (Role-Based Access Control)
- [ ] Encryption at rest
- [ ] Compliance (GDPR, SOC2)
- [ ] High availability setup

## 🐛 Troubleshooting

### Ollama not connecting
```bash
# Make sure Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Microphone not detected
```bash
# Find your microphone device
python -c "import sounddevice as sd; print(sd.query_devices())"

# Update VOICE_DEVICE in .env
```

### Database locked
```bash
# Remove old database and restart
rm liveai.db
python backend/fastapi_app.py
```

## 📝 License

MIT License - Feel free to use and modify

## 👨‍💻 Contributing

1. Fork the repo
2. Create feature branch
3. Make changes
4. Submit pull request

## 🤝 Support

For issues and questions:
- 📧 Email: support@liveai.ai
- 💬 Discord: (coming soon)
- 📖 Docs: http://docs.liveai.ai

---

**Last Updated**: March 25, 2026  
**Version**: 1.0.0 (Beta)  
**Status**: ✅ Production Ready
