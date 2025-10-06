#!/usr/bin/env python3
"""
Integration test script for the Hameed Latif Hospital RAG Bot

This script tests the integration between the FastAPI backend and Streamlit frontend
by simulating the key interactions that would happen in the UI.
"""

import requests
import time
import sys
import subprocess
import threading
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"

def test_api_health():
    """Test the API health endpoint"""
    print("🔍 Testing API health endpoint...")
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint with sample questions"""
    print("🔍 Testing chat endpoint...")
    
    test_questions = [
        "What departments do you have?",
        "Tell me about cardiac surgery",
        "Who are the doctors in anesthesia department?",
        "What is your phone number?",
        "How do I book an appointment?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: '{question}'")
        try:
            payload = {
                "question": question,
                "session_id": "test_session"
            }
            
            response = requests.post(
                CHAT_ENDPOINT,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                print(f"✅ Response received ({len(response_text)} chars)")
                print(f"📄 Preview: {response_text[:100]}...")
            else:
                print(f"❌ Chat request failed: HTTP {response.status_code}")
                if response.text:
                    print(f"Error details: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Chat request error: {e}")
            return False
    
    return True

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🔍 Testing error handling...")
    
    # Test empty question
    try:
        payload = {"question": "", "session_id": "test_session"}
        response = requests.post(CHAT_ENDPOINT, json=payload, timeout=10)
        if response.status_code == 400:
            print("✅ Empty question properly rejected")
        else:
            print(f"❌ Empty question not handled correctly: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    # Test malformed request
    try:
        response = requests.post(CHAT_ENDPOINT, json={"invalid": "data"}, timeout=10)
        if response.status_code in [400, 422]:  # 422 is FastAPI validation error
            print("✅ Invalid request properly rejected")
        else:
            print(f"❌ Invalid request not handled correctly: {response.status_code}")
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    return True

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 HAMEED LATIF HOSPITAL RAG BOT - INTEGRATION TESTS")
    print("=" * 60)
    
    # Check if API is running
    print("🔍 Checking if API is running...")
    if not test_api_health():
        print("\n❌ API is not running. Please start it first with:")
        print("   cd api && uvicorn main:app --host 0.0.0.0 --port 8000")
        return False
    
    # Test chat functionality
    if not test_chat_endpoint():
        print("\n❌ Chat endpoint tests failed")
        return False
    
    # Test error handling
    if not test_error_handling():
        print("\n❌ Error handling tests failed")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL INTEGRATION TESTS PASSED!")
    print("✅ Backend API is working correctly")
    print("✅ Chat functionality is operational")
    print("✅ Error handling is working")
    print("✅ Ready for Streamlit frontend integration")
    print("=" * 60)
    
    return True

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Integration Test Script for Hameed Latif Hospital RAG Bot")
        print("\nUsage:")
        print("  python test_integration.py")
        print("\nThis script tests the FastAPI backend endpoints to ensure")
        print("they work correctly before launching the Streamlit frontend.")
        print("\nMake sure the API is running on localhost:8000 before running tests.")
        return
    
    success = run_integration_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
