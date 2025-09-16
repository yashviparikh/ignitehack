#!/usr/bin/env python3
"""
⚡ Quick WebSocket Notification Test
Simple test to verify notification delivery
"""

import asyncio
import websockets
import json
import requests
import sys
import sys

async def test_single_ngo_notification():
    """Quick test with one NGO connection"""
    
    print("⚡ QUICK NOTIFICATION TEST")
    print("="*40)
    
    # Connect to NGO WebSocket (NGO ID 1)
    ngo_id = 1
    uri = f"ws://localhost:8000/ws/ngo/{ngo_id}"
    websocket = None
    
    try:
        print(f"🔌 Connecting to NGO {ngo_id}...")
        websocket = await websockets.connect(uri)
        print(f"✅ Connected to NGO {ngo_id}")
        
        # Listen for notifications in background
        notification_received = None
        
        async def listen():
            nonlocal notification_received
            try:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    print(f"\n🔔 NOTIFICATION RECEIVED!")
                    print(f"📊 {json.dumps(data, indent=2)}")
                    notification_received = data
                    break  # Exit after first notification
            except websockets.exceptions.ConnectionClosed:
                print(f"🔌 WebSocket connection closed")
            except Exception as e:
                print(f"❌ Listen error: {e}")
        
        listen_task = asyncio.create_task(listen())
        
        # Wait a moment then create donation
        await asyncio.sleep(1)
        
        print(f"🍽️ Creating test donation...")
        donation = {
            "restaurant_name": "Quick Test Restaurant", 
            "food_type": "Prepared Meals",
            "food_description": "Test notification food",
            "quantity": 10,
            "latitude": 12.9716,
            "longitude": 77.5946,
            "pickup_address": "Test Address",
            "donor_user": "quick_tester"
        }
        
        response = requests.post("http://localhost:8000/api/donations/", json=donation)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Donation created: ID {result.get('id')}")
            
            # Wait for notification (with timeout)
            try:
                await asyncio.wait_for(listen_task, timeout=10.0)
                if notification_received:
                    print(f"✅ SUCCESS! Notification received")
                    return True
                else:
                    print(f"❌ No notification received")
                    return False
            except asyncio.TimeoutError:
                print(f"⏰ TIMEOUT! No notification received within 10 seconds")
                return False
        else:
            print(f"❌ Failed to create donation: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    finally:
        try:
            if websocket is not None:
                await websocket.close()
        except:
            pass

if __name__ == "__main__":
    try:
        result = asyncio.run(test_single_ngo_notification())
        if result:
            print(f"\n🎉 NOTIFICATION SYSTEM WORKS!")
            sys.exit(0)
        else:
            print(f"\n⚠️ NOTIFICATION SYSTEM ISSUE")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Test interrupted")
        sys.exit(1)