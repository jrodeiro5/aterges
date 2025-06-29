# Aterges Backend API

**FastAPI backend for the Aterges AI Platform**

[![Status](https://img.shields.io/badge/Phase%200-Complete-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.13.3-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-green)]()
[![Database](https://img.shields.io/badge/Database-Supabase-orange)]()

---

## 🎯 **Overview**

The Aterges backend provides secure authentication, database management, and will power the AI orchestration system. Built with FastAPI for high performance and async support.

## ✅ **Current Status (Phase 0 Complete)**

- ✅ **Authentication System** - JWT with Supabase integration
- ✅ **Database Integration** - PostgreSQL via Supabase
- ✅ **API Endpoints** - Health, auth, protected routes
- ✅ **Security** - CORS, RLS, password hashing
- ✅ **Development Environment** - Local server running
- 🔄 **Cloud Deployment** - Ready for Google Cloud Run

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.13+
- Virtual environment tool
- Supabase account (already configured)

### **Local Development**
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start development server
python main.py
```

### **Available URLs**
- **API Server:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 📋 **API Endpoints**

### **Authentication**
```bash
POST /auth/signup     # User registration
POST /auth/login      # User authentication  
POST /auth/logout     # User logout
```

### **Protected Routes**
```bash
GET  /api/me          # Get current user info (requires auth)
POST /api/query       # Chat endpoint (placeholder for Phase 1)
```

### **System**
```bash
GET  /health          # Health check
```

---

## 🏗️ **Architecture**

### **Current Structure**
```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and environment variables
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (local)
├── auth/
│   ├── auth_service.py    # Authentication logic
│   └── models.py          # Pydantic models for auth
├── database/
│   └── database.py        # Database connection and queries
└── scripts/
    ├── dev.bat           # Windows development starter
    ├── dev.sh            # Unix development starter
    └── test-config.py    # Configuration validator
```

### **Phase 1 Planned Structure**
```
backend/
├── ai/                    # AI orchestration (Phase 1)
│   ├── orchestrator.py   # Main AI logic controller
│   ├── models.py         # AI model integrations
│   └── tool_calling.py   # Tool calling workflow
├── agents/               # Data agents (Phase 1)
│   ├── base_agent.py    # Base agent class
│   ├── google_analytics_agent.py
│   └── __init__.py      # Agent registry
└── [existing structure]
```

---

## 🔐 **Security Features**

### **Implemented**
- ✅ **JWT Authentication** with configurable expiration
- ✅ **Password Hashing** using bcrypt
- ✅ **CORS Configuration** for cross-origin requests
- ✅ **Environment Variable Protection**
- ✅ **Supabase RLS Integration**

### **Configuration**
```python
# Key security settings in config.py
SECRET_KEY = "your-secure-jwt-secret"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
CORS_ORIGINS = ["http://localhost:3000", "https://aterges.vercel.app"]
```

---

## 🗄️ **Database Schema**

### **Tables**
- **`profiles`** - User profile information
- **`integrations`** - BYOK API keys and configurations
- **`conversations`** - Chat conversation history
- **`messages`** - Individual chat messages

### **Relationships**
```sql
profiles      1:N → conversations
conversations 1:N → messages
profiles      1:N → integrations
```

### **Security**
- **Row Level Security (RLS)** enabled on all tables
- **Foreign key constraints** with performance indexes
- **Automatic timestamps** with triggers

---

## ⚙️ **Environment Configuration**

### **Required Variables**
```bash
# Application
DEBUG=true
SECRET_KEY=your-jwt-secret-key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
DATABASE_URL=your-postgres-connection-string

# Google Cloud (Phase 1)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path-to-service-account.json

# API Configuration
CORS_ORIGINS=http://localhost:3000,https://aterges.vercel.app
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### **Environment Files**
- **`.env`** - Local development (gitignored)
- **`.env.example`** - Template with placeholder values
- **Production** - Set via cloud provider environment variables

---

## 🔄 **Development Workflow**

### **Starting Development**
```bash
# Method 1: Quick start
dev.bat  # Windows
./dev.sh # macOS/Linux

# Method 2: Manual
python main.py

# Method 3: With config validation
python test-config.py  # Test configuration first
python main.py         # Then start server
```

### **Testing**
```bash
# Test configuration
python test-config.py

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Test authentication
# Use the interactive docs at /docs
```

---

## 📦 **Dependencies**

### **Core Framework**
- **FastAPI 0.115.11** - High-performance async web framework
- **Uvicorn** - ASGI server for FastAPI
- **Pydantic** - Data validation and serialization

### **Database & Auth**
- **Supabase 2.9.1** - Backend-as-a-Service client
- **AsyncPG** - Async PostgreSQL adapter
- **PyJWT** - JSON Web Token implementation
- **Bcrypt** - Password hashing

### **Phase 1 Dependencies**
- **Google Cloud AI Platform** - Vertex AI integration
- **Google Analytics Data API** - GA4 data retrieval
- **Google Auth** - Service account authentication

---

## 🚀 **Deployment**

### **Local Development** ✅
- **Status:** Working
- **URL:** http://localhost:8000
- **Environment:** `.env` file

### **Google Cloud Run** (Planned)
- **Configuration:** `Dockerfile` ready
- **CI/CD:** GitHub Actions workflow configured
- **Environment:** Cloud secrets management
- **Scaling:** Automatic based on demand

### **Deployment Commands**
```bash
# Build Docker image
docker build -t aterges-backend .

# Run locally in container
docker run -p 8000:8000 aterges-backend

# Deploy to Google Cloud Run (requires GCP setup)
gcloud run deploy aterges-backend \
  --image gcr.io/PROJECT-ID/aterges-backend \
  --platform managed \
  --allow-unauthenticated
```

---

## 🔮 **Phase 1 Development Plan**

### **AI Orchestrator Implementation**
```python
# ai/orchestrator.py
class AIOrchestrator:
    def __init__(self):
        self.gemini_client = VertexAI()
        self.agent_registry = AgentRegistry()
    
    async def process_query(self, user_query: str) -> str:
        # 1. Send query to Gemini with available tools
        # 2. Parse tool calling response
        # 3. Execute requested agent
        # 4. Send results back to Gemini for synthesis
        # 5. Return human-readable response
```

### **Google Analytics Agent**
```python
# agents/google_analytics_agent.py
class GoogleAnalyticsAgent(BaseAgent):
    def __init__(self, credentials):
        self.analytics = AnalyticsDataApiClient(credentials)
    
    async def query_ga4(self, metrics, dimensions, date_ranges):
        # Query GA4 API and return structured data
```

### **API Enhancement**
```python
# Update main.py /api/query endpoint
@app.post("/api/query")
async def query_ai(query_data: dict, current_user = Depends(get_current_user)):
    orchestrator = AIOrchestrator()
    response = await orchestrator.process_query(query_data["prompt"])
    
    # Save conversation to database
    await save_conversation(current_user["id"], query_data["prompt"], response)
    
    return {"response": response}
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Python Module Errors**
```bash
# Missing dependencies
pip install -r requirements.txt

# Missing email validator
pip install pydantic[email]
```

#### **Database Connection Issues**
```bash
# Test database connection
python test-config.py

# Check environment variables
echo $SUPABASE_URL
echo $DATABASE_URL
```

#### **Port Already in Use**
```bash
# Kill process on port 8000
taskkill /F /PID $(netstat -ano | findstr :8000)  # Windows
kill $(lsof -t -i:8000)  # macOS/Linux
```

### **Development Tips**
- **Use `test-config.py`** to validate environment before starting
- **Check logs** for detailed error information
- **Use `/docs`** for interactive API testing
- **Enable debug mode** in development for detailed error traces

---

## 📊 **Performance**

### **Current Metrics**
- ⚡ **<100ms** API response times
- 🔄 **Async/await** for all I/O operations
- 📊 **Connection pooling** for database efficiency
- 🛡️ **JWT caching** for authentication performance

### **Phase 1 Optimization Plan**
- 🤖 **AI response caching** for common queries
- 📈 **Background processing** for complex analytics
- 🔄 **Streaming responses** for real-time chat
- 📊 **Query result caching** for Google APIs

---

## 📞 **Support**

### **Development Issues**
- **Configuration:** Use `test-config.py` to diagnose issues
- **API Testing:** Use interactive docs at `/docs`
- **Database:** Check Supabase dashboard for connection issues

### **Next Phase**
- **AI Integration:** Requires Google Cloud setup
- **Agent Development:** Implement data connectors
- **Cloud Deployment:** Configure GitHub Actions secrets

---

**Ready for Phase 1: AI Orchestrator Development! 🤖**

*The foundation is solid - now let's build the intelligence layer*
