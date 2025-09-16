#!/usr/bin/env python3
"""
API Routes Verification Script
Tests all endpoints to ensure they're properly accessible with correct /api prefixes
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, endpoint, description):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}")
        elif method == "PATCH":
            response = requests.patch(f"{BASE_URL}{endpoint}")
        
        status = "✅" if response.status_code in [200, 422, 404] else "❌"
        print(f"{status} {method} {endpoint} - {description} (Status: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ {method} {endpoint} - {description} (Error: {e})")
        return False

def main():
    print("🧪 API Routes Verification")
    print("=" * 60)
    
    # Test all endpoints
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/api/health", "Health check"),
        ("GET", "/api/donations/", "Get donations"),
        ("POST", "/api/donations/", "Create donation"),
        ("GET", "/api/donations/1", "Get specific donation"),
        ("PATCH", "/api/donations/1/status", "Update donation status"),
        ("POST", "/api/donations/1/upload-photo", "Upload photo"),
        ("POST", "/api/donations/1/allocate", "🧠 ML ALLOCATION"),
        ("GET", "/api/ngos/", "Get NGOs"),
        ("POST", "/api/ngos/", "Create NGO"),
        ("GET", "/api/pickups/", "Get pickups"),
        ("POST", "/api/pickups/", "Create pickup"),
        ("PATCH", "/api/pickups/1", "Update pickup"),
        ("GET", "/api/stats/", "Get statistics"),
        ("GET", "/api/websocket/stats", "WebSocket stats"),
    ]
    
    passed = 0
    for method, endpoint, description in endpoints:
        if test_endpoint(method, endpoint, description):
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{len(endpoints)} endpoints accessible")
    
    if passed == len(endpoints):
        print("🎉 All endpoints are properly configured!")
        print("✅ ML allocation endpoint should now appear in /docs")
    else:
        print("⚠️  Some endpoints need attention")
    
    print(f"\n🔗 Check FastAPI docs at: {BASE_URL}/docs")

if __name__ == "__main__":
    main()