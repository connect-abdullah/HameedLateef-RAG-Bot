from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import sys
from pathlib import Path
import uvicorn

# Add parent directory to path to import from project root
sys.path.append(str(Path(__file__).parent.parent))

# Import the chatbot function from the existing chatbot.py
from chatbot import ask_question

# Global variable to track if components are loaded
chatbot_ready = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize chatbot components by importing from chatbot.py"""
    global chatbot_ready
    
    print("FastAPI starting up...")
    print("Chatbot components will be loaded from chatbot.py when first used")
    chatbot_ready = True
    
    # Yield control back to FastAPI
    yield
    
    # Cleanup
    print("FastAPI shutting down...")

app = FastAPI(
    title="Hameed Latif Hospital Chatbot API",
    description="API for the Hameed Latif Hospital chatbot assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    question: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Hameed Latif Hospital Chatbot API is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint to get responses from the chatbot"""
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Use the existing ask_question function from chatbot.py
        response = ask_question(request.question)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id
        )
        
    except Exception as e:
        print(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    try:
        return {
            "status": "healthy" if chatbot_ready else "starting",
            "message": "FastAPI server is running and ready to handle chat requests"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Health check failed"
        }

if __name__ == "__main__":
  uvicorn.run(app, host="0.0.0.0", port=8000) 