"""
Test WebSocket functionality with the integrated main.py server
"""

import asyncio
import websockets
import json
import requests
import time

async def test_websocket_real_time():
    """Test WebSocket connection and real-time updates"""
    print("🧪 Testing integrated WebSocket functionality...")
    
    try:
        # Connect to WebSocket
        uri = "ws://127.0.0.1:8000/ws"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a ping to test communication
            ping_msg = {"type": "ping", "timestamp": time.time()}
            await websocket.send(json.dumps(ping_msg))
            print("📤 Sent ping message")
            
            # Set up a listener for messages
            async def listen_for_updates():
                try:
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"📥 Received: {data}")
                        
                        if data.get("type") == "pong":
                            print("✅ Ping/pong successful!")
                        elif data.get("type") == "new_donation":
                            print(f"📢 New donation alert: {data['data']['restaurant_name']}")
                        elif data.get("type") == "status_update":
                            print(f"📢 Status update: Donation {data['data']['donation_id']} → {data['data']['new_status']}")
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 WebSocket connection closed")
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
            
            # Start listening in background
            listen_task = asyncio.create_task(listen_for_updates())
            
            # Wait a moment for ping response
            await asyncio.sleep(1)
            
            # Test creating a donation via HTTP API to trigger WebSocket broadcast
            print("\n🧪 Creating test donation to trigger WebSocket broadcast...")
            
            donation_data = {
                "restaurant_name": "WebSocket Test Restaurant",
                "food_description": "Test food for WebSocket broadcasting",
                "quantity": 5,
                "food_type": "Test Food",
                "expiry_hours": 12,
                "pickup_address": "123 Test Street"
            }
            
            # Create donation via HTTP API
            response = requests.post("http://127.0.0.1:8000/api/donations/", json=donation_data)
            
            if response.status_code == 200:
                result = response.json()
                donation_id = result["id"]
                print(f"✅ Test donation created with ID: {donation_id}")
                
                # Wait for WebSocket broadcast
                print("⏳ Waiting for WebSocket broadcast...")
                await asyncio.sleep(2)
                
                # Test status update
                print(f"\n🧪 Testing status update for donation {donation_id}...")
                pickup_data = {
                    "donation_id": donation_id,
                    "ngo_id": 1  # Assuming NGO with ID 1 exists
                }
                
                pickup_response = requests.post("http://127.0.0.1:8000/api/pickups/", json=pickup_data)
                if pickup_response.status_code == 200:
                    print("✅ Pickup created, waiting for status update broadcast...")
                    await asyncio.sleep(2)
                else:
                    print(f"⚠️ Pickup creation failed: {pickup_response.status_code}")
                
            else:
                print(f"❌ Failed to create donation: {response.status_code}")
                print(f"Response: {response.text}")
            
            # Cancel the listening task
            listen_task.cancel()
            
            print("\n✅ WebSocket test completed successfully!")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ WebSocket connection refused - server may not be running")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

def test_http_endpoints():
    """Test HTTP endpoints are working"""
    print("\n🧪 Testing HTTP endpoints...")
    
    endpoints = [
        ("GET", "/api/health", "Health check"),
        ("GET", "/api/donations/", "Get donations"),
        ("GET", "/api/ngos/", "Get NGOs"),
        ("GET", "/api/stats/", "Get statistics"),
        ("GET", "/api/ws/stats", "WebSocket stats")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://127.0.0.1:8000{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {description}: {response.status_code}")
                if endpoint == "/api/ws/stats":
                    data = response.json()
                    print(f"   📊 WebSocket connections: {data}")
            else:
                print(f"⚠️ {description}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: {e}")

if __name__ == "__main__":
    print("🚀 Testing integrated WebSocket + HTTP system...\n")
    
    # Test HTTP endpoints first
    test_http_endpoints()
    
    # Test WebSocket functionality
    asyncio.run(test_websocket_real_time())
    
    print("\n🎉 All tests completed!")