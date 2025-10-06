#!/usr/bin/env python3
"""
Hameed Latif Hospital RAG Bot - Complete Application Launcher

This script launches both the FastAPI backend and Streamlit frontend
in a coordinated manner, ensuring the complete application runs smoothly.

Usage:
    python app.py

The script will:
1. Start the FastAPI backend server in a separate process
2. Wait for the backend to be ready
3. Launch the Streamlit frontend
4. Handle graceful shutdown of both services
"""

import subprocess
import sys
import time
import signal
import os
import requests
from pathlib import Path
import threading
import atexit
from typing import Optional

# Configuration
BACKEND_HOST = "0.0.0.0"
BACKEND_PORT = 8000
FRONTEND_PORT = 8501
HEALTH_CHECK_URL = f"http://localhost:{BACKEND_PORT}/health"
MAX_STARTUP_WAIT = 60  # seconds

# Global process references for cleanup
backend_process: Optional[subprocess.Popen] = None
frontend_process: Optional[subprocess.Popen] = None

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🏥 HAMEED LATIF HOSPITAL RAG BOT LAUNCHER 🏥          ║
    ║                                                              ║
    ║              AI-Powered Hospital Assistant                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Basic packages that should import without heavy dependencies
    basic_packages = [
        "fastapi", "uvicorn", "streamlit", "requests", 
        "pandas", "python-dotenv"
    ]
    
    missing_packages = []
    
    for package in basic_packages:
        try:
            __import__(package.replace("-", "_").replace("python_dotenv", "dotenv"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Please install them using: pip install -r requirements.txt")
        return False
    
    # Check for heavy ML packages separately with better error handling
    ml_packages = ["sentence_transformers", "langchain_google_genai", "faiss"]
    
    for package in ml_packages:
        try:
            if package == "faiss":
                # Try both faiss-cpu and faiss-gpu
                try:
                    __import__("faiss")
                except ImportError:
                    try:
                        __import__("faiss_cpu")
                    except ImportError:
                        missing_packages.append("faiss-cpu")
            else:
                __import__(package.replace("-", "_"))
        except Exception as e:
            # For ML packages, we'll warn but not fail completely
            print(f"⚠️  Warning: {package} may have compatibility issues: {str(e)[:100]}...")
            print(f"   The application will attempt to load this during runtime")
    
    if missing_packages:
        print(f"❌ Missing critical packages: {', '.join(missing_packages)}")
        print("📦 Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ Core dependencies are available")
    return True

def check_environment():
    """Check if required environment variables and files exist"""
    print("🔍 Checking environment...")
    
    # Check for required files
    required_files = [
        "backend/main.py",
        "backend/chatbot.py", 
        "frontend/streamlit_app.py",
        "data/hospital_data_with_embeddings.pkl",
        "data/hospital_faiss_index.bin"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check for .env file (optional but recommended)
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found. Make sure GEMINI_API_KEY is set in your environment")
    
    print("✅ Environment check passed")
    return True

def wait_for_backend():
    """Wait for the backend to be ready"""
    print(f"⏳ Waiting for backend to start (max {MAX_STARTUP_WAIT}s)...")
    
    start_time = time.time()
    while time.time() - start_time < MAX_STARTUP_WAIT:
        try:
            response = requests.get(HEALTH_CHECK_URL, timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(".", end="", flush=True)
        time.sleep(1)
    
    print(f"\n❌ Backend failed to start within {MAX_STARTUP_WAIT} seconds")
    return False

def start_backend():
    """Start the FastAPI backend server"""
    global backend_process
    
    print("🚀 Starting FastAPI backend...")
    
    try:
        # Start the backend process
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", BACKEND_HOST,
            "--port", str(BACKEND_PORT),
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"📡 Backend starting on http://{BACKEND_HOST}:{BACKEND_PORT}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the Streamlit frontend"""
    global frontend_process
    
    print("🎨 Starting Streamlit frontend...")
    
    try:
        # Start the frontend process
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "frontend/streamlit_app.py",
            "--server.port", str(FRONTEND_PORT),
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
        
        print(f"🌐 Frontend starting on http://localhost:{FRONTEND_PORT}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def cleanup():
    """Clean up processes on exit"""
    global backend_process, frontend_process
    
    print("\n🧹 Cleaning up processes...")
    
    if frontend_process:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
            print("✅ Frontend stopped")
        except subprocess.TimeoutExpired:
            frontend_process.kill()
            print("🔪 Frontend force-killed")
        except Exception as e:
            print(f"⚠️  Error stopping frontend: {e}")
    
    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
            print("✅ Backend stopped")
        except subprocess.TimeoutExpired:
            backend_process.kill()
            print("🔪 Backend force-killed")
        except Exception as e:
            print(f"⚠️  Error stopping backend: {e}")

def signal_handler(signum, frame):
    """Handle interrupt signals"""
    print(f"\n🛑 Received signal {signum}, shutting down...")
    cleanup()
    sys.exit(0)

def monitor_processes():
    """Monitor backend and frontend processes"""
    global backend_process, frontend_process
    
    while True:
        time.sleep(5)
        
        # Check if backend is still running
        if backend_process and backend_process.poll() is not None:
            print("❌ Backend process died unexpectedly")
            cleanup()
            sys.exit(1)
        
        # Check if frontend is still running
        if frontend_process and frontend_process.poll() is not None:
            print("❌ Frontend process died unexpectedly")
            cleanup()
            sys.exit(1)

def main():
    """Main application launcher"""
    print_banner()
    
    # Register cleanup function
    atexit.register(cleanup)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)
    
    if not check_environment():
        sys.exit(1)
    
    try:
        # Start backend
        if not start_backend():
            sys.exit(1)
        
        # Wait for backend to be ready
        if not wait_for_backend():
            cleanup()
            sys.exit(1)
        
        # Start frontend
        if not start_frontend():
            cleanup()
            sys.exit(1)
        
        print("\n" + "="*60)
        print("🎉 APPLICATION STARTED SUCCESSFULLY!")
        print("="*60)
        print(f"🏥 Hospital Assistant: http://localhost:{FRONTEND_PORT}")
        print(f"📡 API Documentation: http://localhost:{BACKEND_PORT}/docs")
        print(f"❤️  Health Check: http://localhost:{BACKEND_PORT}/health")
        print("="*60)
        print("💡 Tips:")
        print("   • Ask about hospital departments, doctors, or services")
        print("   • Use the sidebar for quick actions and system status")
        print("   • Press Ctrl+C to stop the application")
        print("="*60)
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitor_processes, daemon=True)
        monitor_thread.start()
        
        # Wait for processes to complete
        try:
            if frontend_process:
                frontend_process.wait()
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        cleanup()
        sys.exit(1)
    
    finally:
        cleanup()

if __name__ == "__main__":
    main()
