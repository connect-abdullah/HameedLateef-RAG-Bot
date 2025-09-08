# Hameed Latif Hospital Chatbot API

FastAPI-based REST API for the Hameed Latif Hospital chatbot assistant.

## Features

- 🤖 AI-powered chatbot responses using semantic search
- 🔍 FAISS-based vector search for hospital information
- 💬 Conversation memory to maintain context
- 🌐 CORS-enabled for frontend integration
- 📋 Comprehensive health checks

## Installation

1. Install dependencies:

```bash
pip install -r ../requirements.txt
```

2. Make sure you have the required data files in the project root:

   - `hospital_data_with_embeddings.pkl`
   - `hospital_faiss_index.bin`
3. Create a `.env` file with your API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Running the API

### Development

```bash
cd api
python main.py
```

### Production

```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST `/chat`

Send a question and get a chatbot response.

**Request Body:**

```json
{
    "question": "What services does the cardiology department offer?",
    "session_id": "user123"
}
```

**Response:**

```json
{
    "response": "Our cardiology department offers comprehensive heart care services including...",
    "session_id": "user123"
}
```

### GET `/health`

Check the health status of all chatbot components.

**Response:**

```json
{
    "status": "healthy",
    "components": {
        "dataframe_loaded": true,
        "faiss_index_loaded": true,
        "embedder_loaded": true,
        "llm_loaded": true,
        "memory_loaded": true
    },
    "message": "All systems operational"
}
```

### GET `/`

Simple health check endpoint.

## Frontend Integration

You can use this API with any frontend framework. Here's a JavaScript example:

```javascript
async function askChatbot(question, sessionId = 'default') {
    const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            session_id: sessionId
        })
    });
  
    const data = await response.json();
    return data.response;
}

// Usage
askChatbot("What are your visiting hours?")
    .then(response => console.log(response));
```

## Error Handling

The API includes comprehensive error handling:

- 400: Bad Request (empty question)
- 500: Internal Server Error (component failures)

## Interactive Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Notes

- The API loads all chatbot components on startup, which may take a few moments
- Memory is maintained per session for conversation context
- CORS is currently set to allow all origins - configure appropriately for production
