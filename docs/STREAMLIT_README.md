# 🏥 Hameed Latif Hospital RAG Bot - Streamlit Frontend

A complete AI-powered hospital assistant with a modern Streamlit frontend and FastAPI backend.

## 🚀 Quick Start

### One-Command Launch
```bash
python app.py
```

This single command will:
- ✅ Check all dependencies and environment
- 🚀 Start the FastAPI backend server
- ⏳ Wait for backend to be ready
- 🎨 Launch the Streamlit frontend
- 🔄 Monitor both services
- 🧹 Handle graceful shutdown

### Manual Launch (Alternative)

If you prefer to run services separately:

1. **Start Backend:**
   ```bash
   cd api
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend:**
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

## 📋 Prerequisites

### Required Files
Ensure these files exist in your project:
- `api/main.py` - FastAPI backend
- `chatbot.py` - RAG implementation
- `streamlit_app.py` - Streamlit frontend
- `hospital_data_with_embeddings.pkl` - Processed hospital data
- `hospital_faiss_index.bin` - FAISS vector index

### Environment Variables
Create a `.env` file with:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### Dependencies
Install all required packages:
```bash
pip install -r requirements.txt
```

## 🎯 Features

### 🤖 AI Chat Assistant
- **Natural Language Processing**: Ask questions in plain English
- **Contextual Responses**: Maintains conversation context
- **Smart Search**: AI-powered semantic search through hospital data
- **Real-time Responses**: Fast, accurate answers about hospital services

### 🏥 Hospital Information
- **Department Details**: Comprehensive information about all departments
- **Doctor Profiles**: Qualifications, specializations, appointment details
- **Medical Procedures**: Detailed procedure information and what to expect
- **Contact Information**: Phone numbers, addresses, appointment booking

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Clean Interface**: Modern, professional hospital-themed design
- **Quick Actions**: Pre-defined questions for common inquiries
- **Chat History**: Persistent conversation history during session
- **Status Monitoring**: Real-time API health checking

### 🔧 System Features
- **Error Handling**: Graceful error handling with user-friendly messages
- **Health Monitoring**: Backend API status monitoring
- **Session Management**: Unique session IDs for conversation tracking
- **Performance Metrics**: Chat statistics and usage analytics

## 🖥️ User Interface

### Main Chat Interface
- **Chat Window**: Clean, WhatsApp-style chat interface
- **Message Input**: Easy-to-use chat input with placeholder text
- **Quick Questions**: Sidebar with common hospital questions
- **Real-time Typing**: Shows "thinking" indicator during processing

### Sidebar Features
- **System Status**: API health check and status display
- **Hospital Info**: Quick access to contact information
- **Quick Actions**: One-click common questions
- **Chat Statistics**: Message counts and session info
- **Clear History**: Reset conversation anytime

### Information Cards
- **Feature Overview**: Cards explaining available features
- **Sample Questions**: Examples of what you can ask
- **Contact Details**: Hospital address, phone, website

## 🔌 API Integration

### Endpoints Used
- `GET /health` - Backend health status
- `POST /chat` - Send questions and receive AI responses

### Error Handling
- **Connection Errors**: Handles API unavailability gracefully
- **Timeout Handling**: Manages slow responses appropriately
- **Validation Errors**: Clear error messages for invalid inputs
- **Server Errors**: User-friendly error reporting

### Request/Response Format
```json
// Request
{
  "question": "What departments do you have?",
  "session_id": "streamlit_1234567890"
}

// Response
{
  "response": "Hameed Latif Hospital has several departments including...",
  "session_id": "streamlit_1234567890"
}
```

## 🛠️ Technical Architecture

### Frontend (Streamlit)
- **Framework**: Streamlit 1.28+
- **Styling**: Custom CSS for modern appearance
- **State Management**: Session state for chat history
- **HTTP Client**: Requests library for API communication

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **AI Engine**: Google Gemini 2.0 Flash Lite
- **Vector Search**: FAISS for semantic similarity
- **Embeddings**: Sentence Transformers (all-mpnet-base-v2)
- **Memory**: LangChain ConversationSummaryMemory

### Data Pipeline
- **Hospital Data**: Scraped and processed hospital information
- **Embeddings**: Pre-computed embeddings for fast search
- **Vector Index**: FAISS index for efficient similarity search
- **Context Building**: Relevant information retrieval for AI responses

## 🎮 Usage Examples

### Common Questions
```
"What departments do you have?"
"Show me cardiac surgeons"
"How do I book an appointment?"
"What are your emergency services?"
"Tell me about Dr. Smith"
"What procedures do you offer for heart problems?"
```

### Advanced Queries
```
"I have chest pain, which doctor should I see?"
"What's the difference between anesthesia types?"
"Do you have 24/7 emergency services?"
"What insurance do you accept?"
"How do I prepare for heart surgery?"
```

## 🔍 Troubleshooting

### Common Issues

**Backend Won't Start**
- Check if port 8000 is available
- Verify all dependencies are installed
- Ensure data files exist (pkl, bin files)
- Check GEMINI_API_KEY environment variable

**Frontend Connection Error**
- Verify backend is running on port 8000
- Check API health endpoint: http://localhost:8000/health
- Ensure no firewall blocking connections

**Slow Responses**
- Check internet connection (Gemini API calls)
- Verify FAISS index file integrity
- Monitor system resources (RAM, CPU)

**Empty Responses**
- Check Gemini API key validity
- Verify hospital data files are not corrupted
- Check backend logs for errors

### Debug Mode
Run with debug information:
```bash
# Backend with debug
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# Frontend with debug
streamlit run streamlit_app.py --logger.level debug
```

## 📊 Performance

### Expected Performance
- **Response Time**: 2-5 seconds for typical queries
- **Concurrent Users**: Supports multiple simultaneous users
- **Memory Usage**: ~500MB for loaded models and data
- **Startup Time**: 30-60 seconds for initial model loading

### Optimization Tips
- Keep data files on SSD for faster loading
- Ensure adequate RAM (4GB+ recommended)
- Use stable internet connection for Gemini API
- Close unnecessary applications to free resources

## 🔒 Security

### API Security
- CORS configured for frontend access
- Input validation on all endpoints
- Error handling prevents information leakage
- Session isolation between users

### Data Privacy
- No persistent storage of user conversations
- Session data cleared on restart
- Hospital data is anonymized where appropriate
- No personal health information stored

## 🚀 Deployment

### Local Development
- Use `python app.py` for development
- Both services auto-reload on code changes
- Debug mode enabled by default

### Production Deployment
- Configure proper CORS origins
- Use production ASGI server (Gunicorn + Uvicorn)
- Set up reverse proxy (Nginx)
- Configure SSL certificates
- Monitor with proper logging

### Docker Deployment (Future)
```dockerfile
# Example Dockerfile structure
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000 8501
CMD ["python", "app.py"]
```

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run tests: `python -m pytest`
5. Start development: `python app.py`

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for functions
- Keep functions focused and small

## 📝 License

This project is part of the Hameed Latif Hospital RAG Bot system.

## 🆘 Support

For technical support or questions:
- Check the troubleshooting section above
- Review backend logs for error details
- Ensure all prerequisites are met
- Verify API connectivity and health status

---

**Built with ❤️ for Hameed Latif Hospital**
