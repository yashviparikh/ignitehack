"""
Simple HTTP Test to verify server is running
"""

import requests

def test_server():
    try:
        response = requests.get("http://127.0.0.1:8000/")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Server is running!")
            try:
                json_response = response.json()
                print(f"JSON Response: {json_response}")
                return True
            except Exception as json_error:
                print(f"⚠️ Server running but response not JSON: {json_error}")
                return True  # Server is running, just not JSON response
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_donations_endpoint():
    try:
        response = requests.get("http://127.0.0.1:8000/donations/")
        print(f"✅ Donations endpoint: {response.status_code}")
        print(f"Number of donations: {len(response.json())}")
        return True
    except Exception as e:
        print(f"❌ Donations endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing HTTP endpoints...")
    if test_server():
        test_donations_endpoint()
        print("\n💡 Server is working! The WebSocket issue might be due to:")
        print("   1. Server needs restart to apply WebSocket changes")
        print("   2. WebSocket endpoint configuration") 
        print("   3. Port or routing issues")
        print("\n🔄 Please restart your server and try again!")
    else:
        print("❌ Server is not responding - please check if it's running")