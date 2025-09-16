"""
Interactive WebSocket Tester for Food Rescue System
Command-line tool to test WebSocket functionality with custom messages
"""

import asyncio
import websockets
import json
import requests
import sys
from datetime import datetime
import argparse

class WebSocketTester:
    def __init__(self, url="ws://127.0.0.1:8000/ws"):
        self.url = url
        self.websocket = None
        self.connected = False
        
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            print(f"🔌 Connecting to {self.url}...")
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            print("✅ Connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("🔌 Disconnected")
    
    async def send_message(self, message):
        """Send a message to the WebSocket server"""
        if not self.connected:
            print("❌ Not connected to WebSocket")
            return False
            
        try:
            if isinstance(message, dict):
                message_str = json.dumps(message)
            else:
                message_str = str(message)
                
            await self.websocket.send(message_str)
            print(f"📤 Sent: {message_str}")
            return True
        except Exception as e:
            print(f"❌ Send failed: {e}")
            return False
    
    async def listen_for_messages(self, timeout=5):
        """Listen for incoming messages"""
        if not self.connected:
            print("❌ Not connected to WebSocket")
            return None
            
        try:
            print(f"👂 Listening for messages (timeout: {timeout}s)...")
            message = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            try:
                parsed = json.loads(message)
                print(f"📥 Received JSON: {json.dumps(parsed, indent=2)}")
                return parsed
            except json.JSONDecodeError:
                print(f"📥 Received text: {message}")
                return message
        except asyncio.TimeoutError:
            print("⏰ No message received within timeout")
            return None
        except Exception as e:
            print(f"❌ Listen failed: {e}")
            return None
    
    async def ping_test(self):
        """Test ping/pong functionality"""
        ping_msg = {
            "type": "ping",
            "timestamp": datetime.now().isoformat(),
            "test": "ping_test"
        }
        
        print("\n🏓 Testing ping/pong...")
        await self.send_message(ping_msg)
        response = await self.listen_for_messages(timeout=5)
        
        if response and response.get("type") == "pong":
            print("✅ Ping/pong test PASSED!")
            return True
        else:
            print("❌ Ping/pong test FAILED!")
            return False
    
    async def trigger_donation_test(self):
        """Create a donation and test real-time notifications"""
        print("\n🧪 Testing donation notification...")
        
        # Create test donation via HTTP API
        test_donation = {
            "restaurant_name": f"Test Restaurant {datetime.now().strftime('%H:%M:%S')}",
            "food_description": "WebSocket test donation",
            "quantity": 3,
            "food_type": "Test Food",
            "expiry_hours": 12
        }
        
        try:
            print("📝 Creating test donation via API...")
            response = requests.post("http://127.0.0.1:8000/api/donations/", json=test_donation, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Donation created: ID {result['id']}")
                
                # Listen for WebSocket notification
                notification = await self.listen_for_messages(timeout=10)
                
                if notification and notification.get("type") == "new_donation":
                    print("🎉 Real-time notification test PASSED!")
                    print(f"   Notification data: {notification['data']['restaurant_name']}")
                    return True
                else:
                    print("❌ No donation notification received")
                    return False
            else:
                print(f"❌ API request failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Donation test failed: {e}")
            return False
    
    async def custom_message_test(self, message_type, data):
        """Send a custom message and listen for response"""
        print(f"\n📨 Testing custom message: {message_type}")
        
        custom_msg = {
            "type": message_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        await self.send_message(custom_msg)
        response = await self.listen_for_messages(timeout=5)
        
        if response:
            print(f"✅ Received response for {message_type}")
            return response
        else:
            print(f"⚠️ No response for {message_type}")
            return None
    
    async def interactive_mode(self):
        """Interactive mode for manual testing"""
        print("\n🎮 Interactive Mode - Enter messages to send (type 'quit' to exit)")
        print("Commands:")
        print("  ping                    - Send ping message")
        print("  donation                - Trigger donation test")
        print("  listen                  - Listen for messages")
        print("  stats                   - Get WebSocket stats")
        print("  custom:<type>:<data>    - Send custom message")
        print("  quit                    - Exit interactive mode")
        
        while self.connected:
            try:
                command = input("\n💬 Enter command: ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "ping":
                    await self.ping_test()
                elif command == "donation":
                    await self.trigger_donation_test()
                elif command == "listen":
                    await self.listen_for_messages(timeout=10)
                elif command == "stats":
                    await self.get_ws_stats()
                elif command.startswith("custom:"):
                    parts = command.split(":", 2)
                    if len(parts) >= 3:
                        msg_type = parts[1]
                        data = parts[2]
                        await self.custom_message_test(msg_type, data)
                    else:
                        print("❌ Custom format: custom:<type>:<data>")
                elif command:
                    # Send raw message
                    await self.send_message(command)
                    await self.listen_for_messages(timeout=3)
                    
            except KeyboardInterrupt:
                print("\n🛑 Interrupted")
                break
            except EOFError:
                print("\n🛑 EOF")
                break
    
    async def get_ws_stats(self):
        """Get WebSocket connection statistics"""
        try:
            response = requests.get("http://127.0.0.1:8000/api/ws/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                print(f"\n📊 WebSocket Statistics:")
                print(f"   Total connections: {stats['total_connections']}")
                print(f"   NGO connections: {stats['ngo_connections']}")
                print(f"   Donor connections: {stats['donor_connections']}")
                print(f"   Connected NGOs: {stats['connected_ngos']}")
                return stats
            else:
                print(f"❌ Stats request failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Stats request error: {e}")

async def main():
    parser = argparse.ArgumentParser(description="WebSocket Tester for Food Rescue System")
    parser.add_argument("--url", default="ws://127.0.0.1:8000/ws", help="WebSocket URL")
    parser.add_argument("--mode", choices=["test", "interactive", "ping", "donation"], 
                       default="test", help="Test mode")
    parser.add_argument("--timeout", type=int, default=5, help="Message timeout in seconds")
    
    args = parser.parse_args()
    
    tester = WebSocketTester(args.url)
    
    # Connect to WebSocket
    if not await tester.connect():
        sys.exit(1)
    
    try:
        if args.mode == "ping":
            await tester.ping_test()
        elif args.mode == "donation":
            await tester.trigger_donation_test()
        elif args.mode == "interactive":
            await tester.interactive_mode()
        else:  # test mode
            print("🧪 Running full test suite...")
            
            # Get initial stats
            await tester.get_ws_stats()
            
            # Test ping/pong
            ping_result = await tester.ping_test()
            
            # Test donation notifications
            donation_result = await tester.trigger_donation_test()
            
            # Test custom message
            await tester.custom_message_test("test_message", "Hello WebSocket!")
            
            # Final stats
            await tester.get_ws_stats()
            
            print(f"\n📋 Test Results:")
            print(f"   Ping/Pong: {'✅ PASS' if ping_result else '❌ FAIL'}")
            print(f"   Donations: {'✅ PASS' if donation_result else '❌ FAIL'}")
            
            if ping_result and donation_result:
                print("\n🎉 All tests PASSED! WebSocket is working correctly.")
            else:
                print("\n❌ Some tests FAILED! Check the server configuration.")
    
    finally:
        await tester.disconnect()

if __name__ == "__main__":
    print("🚀 Food Rescue WebSocket Tester")
    print("=" * 40)
    asyncio.run(main())