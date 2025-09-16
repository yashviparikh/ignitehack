#!/usr/bin/env python3
"""
🔔 WebSocket Notification System Tester
Tests the smart notification system for ML-matched NGOs
"""

import asyncio
import websockets
import json
import requests
import time
from datetime import datetime

# Server configuration
SERVER_URL = "localhost:8000"
HTTP_BASE = f"http://{SERVER_URL}"
WS_BASE = f"ws://{SERVER_URL}"

class NotificationTester:
    def __init__(self):
        self.ngo_connections = {}
        self.received_notifications = {}
        
    async def connect_ngo(self, ngo_id: int, ngo_name: str):
        """Connect an NGO to the WebSocket notification system"""
        try:
            uri = f"{WS_BASE}/ws/ngo/{ngo_id}"
            print(f"🔌 Connecting NGO {ngo_id} ({ngo_name}) to {uri}")
            
            websocket = await websockets.connect(uri)
            self.ngo_connections[ngo_id] = websocket
            self.received_notifications[ngo_id] = []
            
            print(f"✅ NGO {ngo_id} ({ngo_name}) connected successfully!")
            
            # Start listening for notifications
            asyncio.create_task(self.listen_for_notifications(ngo_id, ngo_name, websocket))
            
            return websocket
            
        except Exception as e:
            print(f"❌ Failed to connect NGO {ngo_id}: {e}")
            return None
    
    async def listen_for_notifications(self, ngo_id: int, ngo_name: str, websocket):
        """Listen for incoming notifications for an NGO"""
        try:
            print(f"👂 NGO {ngo_id} ({ngo_name}) listening for notifications...")
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    self.received_notifications[ngo_id].append(data)
                    
                    print(f"\n🔔 NOTIFICATION RECEIVED!")
                    print(f"📍 NGO: {ngo_id} ({ngo_name})")
                    print(f"📊 Data: {json.dumps(data, indent=2)}")
                    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
                    
                    if data.get("type") == "allocation":
                        donation = data.get("donation", {})
                        print(f"🍽️ Donation ID: {donation.get('id')}")
                        print(f"🏪 Restaurant: {donation.get('restaurant_name')}")
                        print(f"📦 Food: {donation.get('food_description')}")
                        print(f"🎯 Priority Score: {donation.get('priority_score')}")
                        print(f"📍 Distance: {donation.get('distance_km')} km")
                    
                    print("="*50)
                    
                except json.JSONDecodeError:
                    print(f"⚠️ NGO {ngo_id}: Received invalid JSON: {message}")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 NGO {ngo_id} ({ngo_name}) connection closed")
        except Exception as e:
            print(f"❌ Error listening for NGO {ngo_id}: {e}")
    
    def create_test_donation(self, restaurant_name: str, food_type: str, food_description: str):
        """Create a test donation to trigger notifications"""
        donation_data = {
            "restaurant_name": restaurant_name,
            "food_type": food_type,
            "food_description": food_description,
            "quantity": 15,
            "latitude": 12.9716,
            "longitude": 77.5946,
            "pickup_address": "Test Address, Test City",
            "donor_user": "notification_tester",
            "expiry_hours": 4
        }
        
        print(f"\n🍽️ Creating test donation...")
        print(f"🏪 Restaurant: {restaurant_name}")
        print(f"📦 Food: {food_description}")
        
        try:
            response = requests.post(f"{HTTP_BASE}/api/donations/", json=donation_data)
            if response.status_code == 200:
                result = response.json()
                donation_id = result.get("id")
                print(f"✅ Donation created successfully! ID: {donation_id}")
                return donation_id
            else:
                print(f"❌ Failed to create donation: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating donation: {e}")
            return None
    
    def get_ngos(self):
        """Get list of available NGOs"""
        try:
            response = requests.get(f"{HTTP_BASE}/api/ngos/")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get NGOs: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting NGOs: {e}")
            return []
    
    async def run_notification_test(self):
        """Run complete notification system test"""
        print("="*60)
        print("🔔 SMART NOTIFICATION SYSTEM TEST")
        print("="*60)
        
        # Get available NGOs
        print("\n📋 Getting available NGOs...")
        ngos = self.get_ngos()
        if not ngos:
            print("❌ No NGOs found! Please ensure NGOs are registered.")
            return
        
        print(f"✅ Found {len(ngos)} NGOs")
        for ngo in ngos[:5]:  # Show first 5
            print(f"   • NGO {ngo['id']}: {ngo['name']}")
        
        # Connect first 3 NGOs to WebSocket
        print("\n🔌 Connecting NGOs to WebSocket...")
        connected_ngos = []
        for ngo in ngos[:3]:
            websocket = await self.connect_ngo(ngo['id'], ngo['name'])
            if websocket:
                connected_ngos.append(ngo)
        
        if not connected_ngos:
            print("❌ No NGOs connected! Cannot test notifications.")
            return
        
        print(f"✅ {len(connected_ngos)} NGOs connected and listening")
        
        # Wait a moment for connections to stabilize
        print("\n⏳ Waiting for connections to stabilize...")
        await asyncio.sleep(2)
        
        # Create test donations to trigger notifications
        test_donations = [
            ("Pizza Palace", "Prepared Meals", "Fresh hot pizzas ready for pickup"),
            ("Bakery Delight", "Baked Goods", "Assorted pastries and bread"),
            ("Green Garden", "Vegetables", "Fresh organic vegetables"),
        ]
        
        print(f"\n🚀 Creating {len(test_donations)} test donations...")
        
        for i, (restaurant, food_type, description) in enumerate(test_donations, 1):
            print(f"\n--- Test Donation {i}/{len(test_donations)} ---")
            donation_id = self.create_test_donation(restaurant, food_type, description)
            
            if donation_id:
                print(f"⏳ Waiting for ML allocation and notifications...")
                await asyncio.sleep(3)  # Wait for ML processing and notifications
        
        # Wait for any remaining notifications
        print(f"\n⏳ Waiting for any remaining notifications...")
        await asyncio.sleep(5)
        
        # Summary
        print("\n" + "="*60)
        print("📊 NOTIFICATION TEST SUMMARY")
        print("="*60)
        
        total_notifications = 0
        for ngo_id, notifications in self.received_notifications.items():
            ngo_name = next((ngo['name'] for ngo in connected_ngos if ngo['id'] == ngo_id), f"NGO {ngo_id}")
            count = len(notifications)
            total_notifications += count
            
            print(f"📍 {ngo_name} (ID: {ngo_id}): {count} notifications")
            for notification in notifications:
                if notification.get("type") == "allocation":
                    donation = notification.get("donation", {})
                    print(f"   🍽️ Donation {donation.get('id')}: {donation.get('restaurant_name')}")
        
        print(f"\n🎯 Total notifications received: {total_notifications}")
        
        if total_notifications > 0:
            print("✅ NOTIFICATION SYSTEM WORKING!")
            print("🎯 Smart notifications successfully delivered to ML-matched NGOs")
        else:
            print("⚠️ NO NOTIFICATIONS RECEIVED")
            print("🔍 Check server logs for debugging information")
        
        # Close connections
        print(f"\n🔌 Closing connections...")
        for ngo_id, websocket in self.ngo_connections.items():
            await websocket.close()
        
        print("✅ Test completed!")

async def main():
    """Main test function"""
    print("🔔 Smart Notification System Tester")
    print("⏳ Starting in 3 seconds...")
    await asyncio.sleep(3)
    
    tester = NotificationTester()
    await tester.run_notification_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")