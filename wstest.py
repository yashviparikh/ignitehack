import asyncio
import websockets
import json
import random

connected = set()

# Sample donations
donation_samples = [
    {"restaurant": "Pizza Place", "food_type": "Pizza", "quantity": 10, "discounted_price": 50, "location": "123 Main St"},
    {"restaurant": "Bakery", "food_type": "Bread", "quantity": 20, "discounted_price": 30, "location": "456 Market St"},
    {"restaurant": "Sushi Bar", "food_type": "Sushi", "quantity": 15, "discounted_price": 70, "location": "789 Ocean Ave"},
    {"restaurant": "Cafe Delight", "food_type": "Sandwich", "quantity": 12, "discounted_price": 40, "location": "321 Coffee Rd"}
]

async def handler(websocket):
    # Register client
    connected.add(websocket)
    print(f"New client connected. Total clients: {len(connected)}")
    try:
        async for message in websocket:
            # When a client sends a message, broadcast it to all others
            try:
                data = json.loads(message)
                if data.get("type") == "donation_accepted":
                    print(f"Donation accepted: {data['id']}, broadcasting to all clients.")
                    for conn in connected.copy():
                        try:
                            await conn.send(json.dumps(data))
                        except:
                            connected.remove(conn)
            except json.JSONDecodeError:
                print("Received invalid JSON")
    except websockets.ConnectionClosed:
        pass
    finally:
        connected.remove(websocket)
        print(f"Client disconnected. Total clients: {len(connected)}")

async def send_donations():
    while True:
        await asyncio.sleep(random.randint(3, 6))
        donation = random.choice(donation_samples)
        donation_msg = donation.copy()
        donation_msg["id"] = random.randint(100, 999)
        donation_msg["type"] = "new_donation"

        for conn in connected.copy():
            try:
                await conn.send(json.dumps(donation_msg))
            except:
                connected.remove(conn)
        print(f"Sent new donation: {donation_msg['id']}")

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("WebSocket server running on ws://localhost:8765")
    await send_donations()  # continuously send donations

asyncio.run(main())
