import asyncio
import websockets
import json
import random

connected = set()

# Sample donations for testing
donation_samples = [
    {"restaurant": "Pizza Place", "food_type": "Pizza", "quantity": 10, "discounted_price": 50, "location": "123 Main St"},
    {"restaurant": "Bakery", "food_type": "Bread", "quantity": 20, "discounted_price": 30, "location": "456 Market St"},
    {"restaurant": "Sushi Bar", "food_type": "Sushi", "quantity": 15, "discounted_price": 70, "location": "789 Ocean Ave"},
    {"restaurant": "Cafe Delight", "food_type": "Sandwich", "quantity": 12, "discounted_price": 40, "location": "321 Coffee Rd"}
]

async def handler(websocket):
    connected.add(websocket)
    try:
        while True:
            await asyncio.sleep(random.randint(3, 6))  # random interval for testing
            donation = random.choice(donation_samples)
            donation_msg = donation.copy()
            donation_msg["id"] = random.randint(100, 999)  # random ID
            donation_msg["type"] = "new_donation"

            # send to all connected clients
            for conn in connected.copy():
                try:
                    await conn.send(json.dumps(donation_msg))
                except:
                    connected.remove(conn)
    finally:
        connected.remove(websocket)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # run forever

asyncio.run(main())
