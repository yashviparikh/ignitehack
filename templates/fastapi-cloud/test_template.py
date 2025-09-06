"""
Quick Test Script for FastAPI Template
=====================================

Test the FastAPI application without database dependencies.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import create_app

def test_fastapi_template():
    """Test FastAPI template functionality."""
    print("🧪 Testing FastAPI Cloud Template...")
    
    try:
        # Create app without database connections
        app = create_app()
        client = TestClient(app)
        
        print("✅ App created successfully")
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint working:")
            print(f"   - Message: {data.get('message')}")
            print(f"   - Version: {data.get('version')}")
            print(f"   - Status: {data.get('status')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
        
        # Test API docs (if enabled)
        response = client.get("/docs")
        if response.status_code == 200:
            print("✅ API documentation available at /docs")
        else:
            print("ℹ️ API docs disabled (production mode)")
        
        print("🎉 FastAPI Template is fully functional!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fastapi_template()
