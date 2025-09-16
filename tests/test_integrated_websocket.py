"""
Test WebSocket functionality for the unified Food Rescue system
"""

import asyncio
import websockets
import json
import requests
from datetime import datetime

async def test_websocket_connection():
    uri = "ws://127.0.0.1:8000/ws"
    
    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a ping to test connection
            ping_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping message")
            
            # Wait for pong response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong = json.loads(response)
                print(f"📥 Received pong: {pong}")
            except asyncio.TimeoutError:
                print("⚠️ No pong response received")
            
            print("\n🧪 Creating test donation to verify real-time updates...")
            
            # Create a test donation via HTTP API
            test_donation = {
                "restaurant_name": "WebSocket Test Restaurant",
                "food_description": "Test food for WebSocket functionality",
                "quantity": 5,
                "food_type": "Test",
                "expiry_hours": 24
            }
            
            # Create donation via API
            response = requests.post("http://127.0.0.1:8000/api/donations/", json=test_donation)
            
            if response.status_code == 200:
                donation_result = response.json()
                print(f"✅ Test donation created: ID {donation_result['id']}")
                
                # Listen for WebSocket notification
                try:
                    print("👂 Listening for real-time notification...")
                    ws_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    notification = json.loads(ws_message)
                    
                    if notification.get("type") == "new_donation":
                        print("🎉 SUCCESS! Received real-time donation notification:")
                        print(f"   Restaurant: {notification['data']['restaurant_name']}")
                        print(f"   Description: {notification['data']['food_description']}")
                        print(f"   Timestamp: {notification['timestamp']}")
                        return True
                    else:
                        print(f"❓ Received different message type: {notification.get('type')}")
                        
                except asyncio.TimeoutError:
                    print("❌ No WebSocket notification received within 10 seconds")
                    
            else:
                print(f"❌ Failed to create test donation: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False
    
    return False

async def test_websocket_stats():
    """Test the WebSocket stats endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/api/ws/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📊 WebSocket Statistics:")
            print(f"   Total connections: {stats['total_connections']}")
            print(f"   NGO connections: {stats['ngo_connections']}")
            print(f"   Donor connections: {stats['donor_connections']}")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats request failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing WebSocket Integration for Food Rescue System")
    print("=" * 50)
    
    # Test WebSocket stats first
    asyncio.run(test_websocket_stats())
    
    # Test WebSocket connection and real-time updates
    success = asyncio.run(test_websocket_connection())
    
    if success:
        print("\n🎉 WebSocket integration test PASSED!")
        print("✅ Real-time updates are working correctly")
        print("✅ Frontend will receive instant notifications")
    else:
        print("\n❌ WebSocket integration test FAILED!")
        print("❗ Please restart the server to apply changes:")
        print("   1. Stop the current server (Ctrl+C)")
        print("   2. Run: python main.py")
        print("   3. Re-run this test")