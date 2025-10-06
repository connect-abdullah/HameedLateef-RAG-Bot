import streamlit as st
import requests
import json
import time
from typing import Dict, Any, List
import plotly.express as px
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

# Page configuration
st.set_page_config(
    page_title="Hameed Latif Hospital Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple CSS styling
st.markdown("""
<style>
    .status-healthy { color: #28a745; font-weight: bold; }
    .status-unhealthy { color: #dc3545; font-weight: bold; }
    .hospital-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_health() -> Dict[str, Any]:
    """Check if the API is running and healthy"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            return {"status": "healthy", "data": response.json()}
        else:
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "connection_error", "error": "Cannot connect to API - make sure backend is running"}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": "Health check timed out (backend may be starting up)"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def send_chat_message(question: str, session_id: str = "streamlit_session") -> Dict[str, Any]:
    """Send a chat message to the API"""
    try:
        payload = {
            "question": question,
            "session_id": session_id
        }
        
        response = requests.post(
            CHAT_ENDPOINT,
            json=payload,
            timeout=120,  # Increased timeout for first model loading
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return {"status": "success", "data": response.json()}
        elif response.status_code == 400:
            return {"status": "error", "error": "Invalid question format"}
        elif response.status_code == 500:
            error_detail = response.json().get("detail", "Internal server error")
            return {"status": "error", "error": f"Server error: {error_detail}"}
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        return {"status": "connection_error", "error": "Cannot connect to API"}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": "Request timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def initialize_session_state():
    """Initialize session state variables"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"streamlit_{int(time.time())}"
    if "api_status" not in st.session_state:
        st.session_state.api_status = None

def display_chat_message(message: Dict[str, str], is_user: bool = False):
    """Display a chat message with simple styling"""
    if is_user:
        st.chat_message("user").write(message['content'])
    else:
        st.chat_message("assistant").write(message['content'])

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.title("🏥 Hameed Latif Hospital Assistant")
    st.caption("AI-powered healthcare companion for hospital information and services")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        
        # API Health Check
        if st.button("🔄 Check API Status", use_container_width=True):
            with st.spinner("Checking API status..."):
                st.session_state.api_status = check_api_health()
        
        # Display API status
        if st.session_state.api_status:
            status = st.session_state.api_status["status"]
            if status == "healthy":
                st.markdown('<p class="status-healthy">✅ API is healthy and ready</p>', unsafe_allow_html=True)
                if "data" in st.session_state.api_status:
                    st.json(st.session_state.api_status["data"])
            else:
                st.markdown('<p class="status-unhealthy">❌ API is not available</p>', unsafe_allow_html=True)
                error_msg = st.session_state.api_status.get("error", "Unknown error")
                st.error(error_msg)
                
                # Show helpful tips based on error type
                if status == "connection_error":
                    st.info("💡 **Tip**: Make sure the backend is running with `python app.py`")
                elif status == "timeout":
                    st.info("💡 **Tip**: The backend may be starting up. Wait a moment and try again.")
                    st.info("🕐 **First startup**: AI models take 30-60 seconds to load initially.")
        else:
            st.info("🔍 Click 'Check API Status' to verify backend connection")
        
        st.divider()
        
        # Hospital Information
        st.header("🏥 Hospital Info")
        st.info("""
        **Hameed Latif Hospital**  
        📍 14- Abu Baker Block, New Garden Town, Lahore  
        📞 +92 (42) 111-000-043  
        🌐 hameedlatifhospital.com
        """)
        
        st.divider()
        
        # Quick Actions
        st.header("⚡ Quick Questions")
        
        quick_questions = [
            "What departments do you have?",
            "Show me cardiac surgeons", 
            "How can I book an appointment?",
            "What are your visiting hours?"
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{question}", use_container_width=True):
                st.session_state.pending_question = question
        
        st.divider()
        
        # Clear Chat
        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    # Main chat area
    st.header("💬 Chat with Hospital Assistant")
    
    # Display chat history
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            display_chat_message(message, message["is_user"])
    else:
        st.info("👋 Welcome! Ask me anything about Hameed Latif Hospital - departments, doctors, services, or appointments.")
        
    # Chat input
    user_input = st.chat_input("Type your question here...")
    
    # Handle pending question from quick actions
    if "pending_question" in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question
    
    # Process user input
    if user_input and user_input.strip():
        # Add user message to history
        st.session_state.chat_history.append({
            "content": user_input,
            "is_user": True,
            "timestamp": time.time()
        })
        
        # Show user message immediately
        display_chat_message({"content": user_input}, is_user=True)
        
        # Get bot response
        # Show different loading message for first question
        if len(st.session_state.chat_history) <= 1:
            loading_message = "🚀 Loading AI models for the first time... This may take 30-60 seconds"
        else:
            loading_message = "🤔 Thinking..."
            
        with st.spinner(loading_message):
            response = send_chat_message(user_input, st.session_state.session_id)
        
        if response["status"] == "success":
            bot_message = response["data"]["response"]
            st.session_state.chat_history.append({
                "content": bot_message,
                "is_user": False,
                "timestamp": time.time()
            })
            display_chat_message({"content": bot_message}, is_user=False)
        else:
            error_message = f"Sorry, I encountered an error: {response['error']}"
            st.session_state.chat_history.append({
                "content": error_message,
                "is_user": False,
                "timestamp": time.time()
            })
            display_chat_message({"content": error_message}, is_user=False)
            st.error(f"Error: {response['error']}")
        
        # Rerun to update the display
        st.rerun()

if __name__ == "__main__":
    main()
