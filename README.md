# 🏥 Hameed Latif Hospital RAG Bot

An AI-powered hospital assistant that provides intelligent responses about hospital services, departments, doctors, and procedures using Retrieval-Augmented Generation (RAG) technology.

## 🌟 Features

- **🤖 AI-Powered Chatbot**: Uses Google Gemini 2.0 Flash Lite for natural language responses
- **🔍 Semantic Search**: FAISS-based vector search for accurate information retrieval
- **💬 Conversation Memory**: Maintains context across conversations
- **🎨 Modern Web Interface**: Clean, responsive Streamlit frontend
- **📡 REST API**: FastAPI backend with comprehensive endpoints
- **🏥 Hospital-Specific**: Tailored for Hameed Latif Hospital services and information

## 🏗️ Project Structure

```
HameedLateef-RAG-Bot/
├── README.md                 # This file - project overview
├── HOW_TO_RUN.md            # Setup and launch instructions
├── requirements.txt          # Python dependencies
├── app.py                   # Main launcher (runs both backend & frontend)
├── .env                     # Environment variables (create this)
│
├── backend/                 # FastAPI backend
│   ├── main.py             # FastAPI application
│   └── chatbot.py          # RAG implementation
│
├── frontend/               # Streamlit frontend
│   └── streamlit_app.py    # Web interface
│
├── data/                   # Hospital data and AI models
│   ├── hospital_data_with_embeddings.pkl
│   ├── hospital_faiss_index.bin
│   ├── hospital_embedding_data.csv
│   ├── hospital_search_data.csv
│   └── final_hospital_data.json
│
├── docs/                   # Documentation
│   ├── STREAMLIT_README.md # Frontend documentation
│   ├── USAGE_GUIDE.md      # User guide
│   └── test_integration.py # Integration tests
│
└── scrapper/              # Data collection tools
    ├── final_corrected_formatter_v3.py
    └── hameedlatif/       # Scrapy project
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Google Gemini API Key
- 4GB+ RAM (for AI models)

### Installation & Launch

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd HameedLateef-RAG-Bot
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. **Launch application**:
   ```bash
   python app.py
   ```

4. **Access the application**:
   - **Web Interface**: http://localhost:8501
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

## 🎯 What You Can Ask

### Hospital Information
- "What departments do you have?"
- "What are your visiting hours?"
- "Where is the hospital located?"
- "What is your phone number?"

### Doctor Information
- "Show me cardiac surgeons"
- "Who are the anesthesia doctors?"
- "Tell me about Dr. [Name]"
- "Which doctors specialize in [condition]?"

### Medical Services
- "What procedures do you offer for heart problems?"
- "Tell me about cardiac surgery"
- "What is anesthesia and how does it work?"
- "Do you have emergency services?"

### Appointments & Procedures
- "How do I book an appointment?"
- "What should I expect during [procedure]?"
- "How do I prepare for surgery?"
- "What insurance do you accept?"

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Google Gemini 2.0**: Large Language Model for natural responses
- **FAISS**: Facebook AI Similarity Search for vector operations
- **Sentence Transformers**: Text embedding generation
- **LangChain**: Framework for LLM applications
- **Pandas**: Data manipulation and analysis

### Frontend
- **Streamlit**: Web app framework for data science
- **Plotly**: Interactive visualizations
- **Custom CSS**: Modern, hospital-themed styling

### Data Pipeline
- **Scrapy**: Web scraping framework for data collection
- **Vector Embeddings**: Semantic search capabilities
- **JSON/CSV/PKL**: Multiple data format support

## 📊 Performance

- **Response Time**: 2-5 seconds (after initial model loading)
- **First Startup**: 30-60 seconds (model initialization)
- **Memory Usage**: ~500MB (loaded models)
- **Concurrent Users**: Supports multiple simultaneous sessions

## 🔒 Security & Privacy

- **No Data Storage**: Conversations are not permanently stored
- **Session Isolation**: Each user session is independent
- **Input Validation**: All inputs are validated and sanitized
- **CORS Protection**: Configurable cross-origin resource sharing

## 🏥 About Hameed Latif Hospital

**Hameed Latif Hospital** is a leading healthcare institution in Lahore, Pakistan, providing comprehensive medical services across multiple specialties.

- **📍 Address**: 14- Abu Baker Block, New Garden Town, Lahore
- **📞 Phone**: +92 (42) 111-000-043
- **🌐 Website**: https://www.hameedlatifhospital.com

### Departments Covered
- Anesthesia and Pain Management
- Cardiac and Vascular Surgery
- Cardiology
- Emergency Medicine
- General Surgery
- Internal Medicine
- Neurology and Neurosurgery
- Obstetrics and Gynecology
- Orthopedic Surgery
- Pediatrics
- Radiology and Imaging
- And many more...

## 📚 Documentation

- **[HOW_TO_RUN.md](HOW_TO_RUN.md)**: Detailed setup and launch instructions
- **[docs/STREAMLIT_README.md](docs/STREAMLIT_README.md)**: Frontend technical documentation
- **[docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md)**: User guide and tips
- **API Docs**: Available at http://localhost:8000/docs when running

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is developed for Hameed Latif Hospital. Please respect the hospital's data and use responsibly.

## 🆘 Support & Troubleshooting

### Common Issues

1. **"Cannot find data files"**: Ensure all files in `data/` directory exist
2. **"API timeout"**: First startup takes time for model loading
3. **"Import errors"**: Check Python version (3.9+) and dependencies
4. **"Port conflicts"**: Modify ports in `app.py` if needed

### Getting Help

1. Check the **[HOW_TO_RUN.md](HOW_TO_RUN.md)** guide
2. Review error messages in terminal
3. Ensure all prerequisites are met
4. Verify API key is correctly set

## 🎉 Acknowledgments

- **Hameed Latif Hospital** for providing comprehensive healthcare data
- **Google Gemini** for advanced language model capabilities
- **Open Source Community** for the amazing tools and frameworks

---

**Built with ❤️ for better healthcare accessibility**