"""
WebSocket Test Script for Food Rescue System
Tests real-time donation updates
"""

import asyncio
import websockets
import json
import requests
from datetime import datetime

# Test configuration
API_BASE = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/general"

async def test_websocket_connection():
    """Test basic WebSocket connection"""
    print("🔌 Testing WebSocket connection...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message
            await websocket.send("test")
            print("📤 Test message sent")
            
            # Wait for any incoming messages for 2 seconds
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                print(f"📨 Received: {message}")
            except asyncio.TimeoutError:
                print("⏱️ No messages received (this is normal)")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def test_real_time_donation_flow():
    """Test complete donation flow with WebSocket notifications"""
    print("\n🧪 Testing real-time donation flow...")
    
    # Connect to WebSocket first
    try:
        websocket = await websockets.connect(WS_URL)
        print("🔌 WebSocket connected for testing")
        
        # Create a test donation via API
        donation_data = {
            "restaurant_name": "Test Restaurant (WebSocket)",
            "food_description": "Test food for WebSocket verification",
            "quantity": 5,
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        print("📤 Creating test donation...")
        response = requests.post(f"{API_BASE}/donations/", json=donation_data)
        
        if response.status_code == 200:
            donation = response.json()
            donation_id = donation["id"]
            print(f"✅ Donation created: ID {donation_id}")
            
            # Wait for WebSocket notification
            print("👂 Listening for WebSocket notification...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                notification = json.loads(message)
                
                print(f"📨 Received WebSocket notification:")
                print(f"   Type: {notification.get('type')}")
                print(f"   Data: {notification.get('data', {}).get('restaurant_name')}")
                
                if notification.get('type') == 'new_donation':
                    print("✅ WebSocket notification for new donation received!")
                else:
                    print("⚠️ Unexpected notification type")
                    
            except asyncio.TimeoutError:
                print("❌ No WebSocket notification received within 5 seconds")
                
        else:
            print(f"❌ Failed to create donation: {response.status_code}")
            
        await websocket.close()
        
    except Exception as e:
        print(f"❌ Real-time test failed: {e}")

async def test_ngo_acceptance_flow():
    """Test NGO acceptance with WebSocket notifications"""
    print("\n🏢 Testing NGO acceptance flow...")
    
    try:
        # First create an NGO
        ngo_data = {
            "name": "Test NGO (WebSocket)",
            "contact_phone": "+1234567890"
        }
        
        ngo_response = requests.post(f"{API_BASE}/ngos/", json=ngo_data)
        if ngo_response.status_code != 200:
            print("❌ Failed to create test NGO")
            return
            
        ngo = ngo_response.json()
        ngo_id = ngo["id"]
        print(f"✅ Test NGO created: ID {ngo_id}")
        
        # Get available donations
        donations_response = requests.get(f"{API_BASE}/donations/?status=available")
        if donations_response.status_code == 200:
            donations = donations_response.json()
            if donations:
                donation_id = donations[0]["id"]
                print(f"📋 Found available donation: ID {donation_id}")
                
                # Connect WebSocket
                websocket = await websockets.connect(WS_URL)
                print("🔌 WebSocket connected for acceptance test")
                
                # Accept the donation
                pickup_data = {
                    "donation_id": donation_id,
                    "ngo_id": ngo_id
                }
                
                print("🤝 Accepting donation...")
                pickup_response = requests.post(f"{API_BASE}/pickups/", json=pickup_data)
                
                if pickup_response.status_code == 200:
                    print("✅ Donation accepted via API")
                    
                    # Wait for WebSocket notification
                    print("👂 Listening for acceptance notification...")
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        notification = json.loads(message)
                        
                        print(f"📨 Received notification:")
                        print(f"   Type: {notification.get('type')}")
                        
                        if notification.get('type') == 'donation_accepted':
                            print("✅ WebSocket notification for donation acceptance received!")
                        else:
                            print("⚠️ Unexpected notification type")
                            
                    except asyncio.TimeoutError:
                        print("❌ No acceptance notification received")
                        
                else:
                    print(f"❌ Failed to accept donation: {pickup_response.status_code}")
                    
                await websocket.close()
                
            else:
                print("❌ No available donations found")
        else:
            print("❌ Failed to get donations")
            
    except Exception as e:
        print(f"❌ NGO acceptance test failed: {e}")

async def main():
    """Run all WebSocket tests"""
    print("🚀 Starting WebSocket Tests for Food Rescue System")
    print("=" * 50)
    
    # Test 1: Basic connection
    connection_ok = await test_websocket_connection()
    
    if connection_ok:
        # Test 2: Real-time donation flow
        await test_real_time_donation_flow()
        
        # Test 3: NGO acceptance flow
        await test_ngo_acceptance_flow()
        
        print("\n" + "=" * 50)
        print("🎉 WebSocket testing completed!")
        print("💡 If you saw notifications above, real-time updates are working!")
        print("🌐 Open your frontend at http://127.0.0.1:8000 in multiple tabs")
        print("   to see live updates in action!")
    else:
        print("\n❌ WebSocket connection failed - check if server is running")

if __name__ == "__main__":
    asyncio.run(main())