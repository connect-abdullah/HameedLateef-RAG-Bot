# 🚀 Quick Start Guide - Hameed Latif Hospital RAG Bot

## ⚡ One-Command Launch

```bash
python app.py
```

That's it! This single command will:
- ✅ Check all dependencies
- 🚀 Start the FastAPI backend
- ⏳ Wait for backend to be ready  
- 🎨 Launch the Streamlit frontend
- 🌐 Open your browser automatically

## 📱 Access Your Application

Once launched, you can access:

- **🏥 Hospital Assistant**: http://localhost:8501
- **📡 API Documentation**: http://localhost:8000/docs
- **❤️ Health Check**: http://localhost:8000/health

## 🎯 What You Can Do

### Ask Natural Questions
```
"What departments do you have?"
"Show me cardiac surgeons"
"How do I book an appointment?"
"What are your emergency services?"
"Tell me about Dr. Smith"
```

### Get Detailed Information
- **Department Details**: Services, procedures, facilities
- **Doctor Profiles**: Qualifications, specializations, contact info
- **Medical Procedures**: What to expect, preparation steps
- **Hospital Info**: Address, phone numbers, visiting hours

### Use Quick Actions
- Click sidebar buttons for common questions
- Check API status in real-time
- View chat statistics
- Clear conversation history

## 🛠️ Troubleshooting

### If Backend Won't Start
```bash
# Check if required files exist
ls hospital_data_with_embeddings.pkl hospital_faiss_index.bin

# Verify environment variable
echo $GEMINI_API_KEY

# Manual backend start
cd api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### If Frontend Won't Connect
```bash
# Check backend health
curl http://localhost:8000/health

# Manual frontend start
streamlit run streamlit_app.py --server.port 8501
```

### If Packages Missing
```bash
# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## 🔧 Advanced Usage

### Environment Setup
Create `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
```

### Custom Configuration
Edit `app.py` to change:
- Backend port (default: 8000)
- Frontend port (default: 8501)
- Startup timeout (default: 60s)

### Testing Integration
```bash
# Run integration tests
python test_integration.py

# Check specific endpoints
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What departments do you have?", "session_id": "test"}'
```

## 🎨 UI Features

### Main Interface
- **Clean Chat UI**: WhatsApp-style messaging
- **Real-time Responses**: Fast AI-powered answers
- **Session Memory**: Maintains conversation context
- **Error Handling**: User-friendly error messages

### Sidebar Features
- **System Status**: API health monitoring
- **Quick Actions**: One-click common questions
- **Hospital Info**: Contact details and address
- **Chat Stats**: Message counts and session info

### Responsive Design
- **Desktop**: Full-width layout with sidebar
- **Tablet**: Responsive columns and navigation
- **Mobile**: Optimized for touch interaction

## 📊 Performance Tips

- **First Launch**: May take 30-60 seconds to load AI models
- **Typical Response**: 2-5 seconds for most questions
- **Memory Usage**: ~500MB for loaded models
- **Concurrent Users**: Supports multiple simultaneous sessions

## 🔒 Security Notes

- No personal data is stored permanently
- Session data is cleared on restart
- API includes CORS protection
- Input validation on all endpoints

## 🆘 Getting Help

### Check Logs
```bash
# Backend logs
tail -f api/logs/app.log

# Frontend logs (in terminal where streamlit runs)
```

### Common Issues
1. **Port conflicts**: Change ports in `app.py`
2. **Missing API key**: Set `GEMINI_API_KEY` environment variable
3. **Slow responses**: Check internet connection for Gemini API
4. **Memory issues**: Ensure 4GB+ RAM available

### Support
- Review error messages in the UI
- Check terminal output for detailed logs
- Verify all prerequisites are met
- Test API endpoints manually if needed

---

**🏥 Built for Hameed Latif Hospital with ❤️**
