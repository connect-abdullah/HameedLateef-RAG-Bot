# 🚀 How to Run - Hameed Latif Hospital RAG Bot

Complete setup and launch guide for the AI-powered hospital assistant.

## 📋 Prerequisites

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: Version 3.9 or higher
- **Memory**: 4GB+ RAM (for AI models)
- **Storage**: 2GB+ free space
- **Internet**: Stable connection (for Google Gemini API)

### Required Accounts

- **Google AI Studio Account**: For Gemini API access
  - Visit: https://makersuite.google.com/
  - Create account and generate API key

## 🛠️ Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd HameedLateef-RAG-Bot
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env  # On Windows: type nul > .env
```

Add your API key to `.env`:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### Step 5: Verify Data Files

Ensure these files exist in the `data/` directory:

- `hospital_data_with_embeddings.pkl`
- `hospital_faiss_index.bin`
- `hospital_embedding_data.csv`
- `hospital_search_data.csv`
- `final_hospital_data.json`

## 🚀 Launch Methods

### Method 1: One-Command Launch (Recommended)

```bash
python app.py
```

This will:

- ✅ Check all dependencies and files
- 🚀 Start FastAPI backend on port 8000
- ⏳ Wait for backend to be ready
- 🎨 Launch Streamlit frontend on port 8501
- 🌐 Open browser automatically
- 🔄 Monitor both services

### Method 2: Manual Launch (Two Terminals)

**Terminal 1 - Backend:**

```bash
# Activate virtual environment
source venv/bin/activate  # or .venv\Scripts\activate on Windows

# Start backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start frontend
streamlit run frontend/streamlit_app.py --server.port 8501
```

### Method 3: Development Mode

For development with auto-reload:

```bash
# Backend with debug logging
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# Frontend with debug mode
streamlit run frontend/streamlit_app.py --server.port 8501 --logger.level debug
```

## 🌐 Access Points

Once launched, access the application at:

| Service                        | URL                          | Description             |
| ------------------------------ | ---------------------------- | ----------------------- |
| **Web Interface**        | http://localhost:8501        | Main Streamlit app      |
| **API Documentation**    | http://localhost:8000/docs   | Interactive API docs    |
| **API Alternative Docs** | http://localhost:8000/redoc  | ReDoc API documentation |
| **Health Check**         | http://localhost:8000/health | Backend status          |
| **Root Endpoint**        | http://localhost:8000/       | Basic API info          |

## ⏱️ Startup Timeline

### First Launch (Cold Start)

1. **0-10 seconds**: Dependency checking and backend startup
2. **10-60 seconds**: AI model loading (sentence transformers, FAISS index)
3. **60-90 seconds**: Frontend initialization and browser opening
4. **90+ seconds**: Ready for use

### Subsequent Launches

1. **0-5 seconds**: Backend startup (models cached)
2. **5-15 seconds**: Frontend initialization
3. **15+ seconds**: Ready for use

## 🎯 Usage Instructions

### First Time Setup

1. **Launch the application** using `python app.py`
2. **Wait for startup** (be patient on first launch)
3. **Open browser** to http://localhost:8501
4. **Check API status** using the sidebar button
5. **Ask your first question** (may take 30-60 seconds initially)

### Using the Web Interface

#### Sidebar Features

- **🔄 Check API Status**: Verify backend connection
- **🏥 Hospital Info**: Quick access to contact details
- **⚡ Quick Actions**: Pre-defined common questions
- **📊 Chat Stats**: Session statistics
- **🗑️ Clear Chat**: Reset conversation

#### Main Chat Interface

- **Type questions** in the input box at the bottom
- **Use quick action buttons** for common queries
- **View conversation history** in the main area
- **Wait for responses** (first question takes longer)

### Sample Questions to Try

```
"What departments do you have?"
"Show me cardiac surgeons"
"How do I book an appointment?"
"What are your visiting hours?"
"Tell me about anesthesia services"
"Who are the doctors in cardiology?"
"What procedures do you offer for heart problems?"
"Where is the hospital located?"
```

## 🔧 Configuration Options

### Port Configuration

Edit `app.py` to change default ports:

```python
BACKEND_PORT = 8000   # FastAPI backend
FRONTEND_PORT = 8501  # Streamlit frontend
```

### Timeout Settings

Adjust timeouts in `frontend/streamlit_app.py`:

```python
# Health check timeout
response = requests.get(HEALTH_ENDPOINT, timeout=10)

# Chat message timeout
response = requests.post(CHAT_ENDPOINT, json=payload, timeout=120)
```

### Model Configuration

Modify AI settings in `backend/chatbot.py`:

```python
# Change Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",  # or "gemini-pro"
    temperature=0.2,                # 0.0-1.0
    max_output_tokens=500,          # response length
)

# Change embedding model
embedder = SentenceTransformer('all-mpnet-base-v2')  # or other models
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. "Cannot find data files"

```bash
# Check if data files exist
ls -la data/

# If missing, ensure you have:
# - hospital_data_with_embeddings.pkl
# - hospital_faiss_index.bin
# - Other CSV/JSON files
```

#### 2. "API timeout" or "Request timed out"

```bash
# This is normal on first startup
# Wait 60-90 seconds for models to load
# Check backend logs for progress
```

#### 3. "Import errors" or "Module not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.9+

# Activate virtual environment
source .venv/bin/activate
```

#### 4. "Port already in use"

```bash
# Find and kill processes using ports
lsof -ti:8000 | xargs kill -9  # Kill backend
lsof -ti:8501 | xargs kill -9  # Kill frontend

# Or change ports in app.py
```

#### 5. "GEMINI_API_KEY not found"

```bash
# Check .env file exists
cat .env

# Verify API key format
echo $GEMINI_API_KEY

# Recreate .env file if needed
echo "GEMINI_API_KEY=your_key_here" > .env
```

#### 6. "Backend not responding"

```bash
# Check backend status
curl http://localhost:8000/health

# Restart backend manually
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Debug Mode

#### Enable Verbose Logging

```bash
# Backend with debug logs
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug

# Frontend with debug info
streamlit run frontend/streamlit_app.py --logger.level debug
```

#### Check System Resources

```bash
# Monitor memory usage
top -p $(pgrep -f "uvicorn\|streamlit")

# Check disk space
df -h

# Monitor network connections
netstat -tlnp | grep -E "(8000|8501)"
```

### Performance Optimization

#### Speed Up Startup

1. **Keep models loaded**: Don't restart frequently
2. **Use SSD storage**: Faster file access
3. **Increase RAM**: 8GB+ recommended for better performance
4. **Stable internet**: For Gemini API calls

#### Reduce Memory Usage

1. **Close other applications**: Free up RAM
2. **Use smaller models**: Modify `backend/chatbot.py`
3. **Limit concurrent users**: Single user for development

## 🔄 Stopping the Application

### Graceful Shutdown

- **Press `Ctrl+C`** in the terminal running `python app.py`
- The launcher will automatically stop both services

### Manual Shutdown

```bash
# Kill all related processes
pkill -f "uvicorn"
pkill -f "streamlit"

# Or kill specific ports
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
```

## 📊 Monitoring and Logs

### Check Application Status

```bash
# Backend health
curl http://localhost:8000/health

# Frontend accessibility
curl http://localhost:8501

# Process status
ps aux | grep -E "(uvicorn|streamlit)"
```

### View Logs

- **Backend logs**: Displayed in terminal running uvicorn
- **Frontend logs**: Displayed in terminal running streamlit
- **Browser console**: F12 → Console tab for frontend errors

## 🚀 Production Deployment

### Environment Variables

```bash
# Production .env
GEMINI_API_KEY=your_production_key
ENVIRONMENT=production
DEBUG=false
```

### Security Considerations

1. **Change CORS settings** in `backend/main.py`
2. **Use HTTPS** with reverse proxy (nginx)
3. **Set proper firewall rules**
4. **Use environment-specific API keys**

### Docker Deployment (Optional)

```dockerfile
# Example Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000 8501
CMD ["python", "app.py"]
```

## 🆘 Getting Help

### Check Documentation

1. **README.md**: Project overview
2. **docs/STREAMLIT_README.md**: Frontend details
3. **docs/USAGE_GUIDE.md**: User guide
4. **API Docs**: http://localhost:8000/docs

### Verify Setup

```bash
# Run integration tests
python docs/test_integration.py

# Check all components
python -c "
import sys
print('Python:', sys.version)
import streamlit, fastapi, sentence_transformers
print('All packages imported successfully!')
"
```

### Support Checklist

Before seeking help, ensure:

- [ ] Python 3.9+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid API key
- [ ] All data files present in `data/` directory
- [ ] Ports 8000 and 8501 are available
- [ ] Stable internet connection
- [ ] Sufficient RAM (4GB+)

---

**🎉 You're all set! Enjoy using the Hameed Latif Hospital RAG Bot!**
