"""
WebSocket Manager for Food Rescue Real-time Updates
Adapted from lanvan clipboard WebSocket system
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime

class FoodRescueConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.ngo_connections: Dict[int, List[WebSocket]] = {}  # NGO ID -> WebSocket connections
        self.donor_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket, connection_type: str = "general", ngo_id: int = None):
        """Connect a WebSocket client"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if connection_type == "ngo" and ngo_id:
            if ngo_id not in self.ngo_connections:
                self.ngo_connections[ngo_id] = []
            self.ngo_connections[ngo_id].append(websocket)
        elif connection_type == "donor":
            self.donor_connections.append(websocket)
            
        print(f"🔌 WebSocket connected: {connection_type} (NGO: {ngo_id if ngo_id else 'N/A'})")

    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        # Remove from donor connections
        if websocket in self.donor_connections:
            self.donor_connections.remove(websocket)
            
        # Remove from NGO connections
        for ngo_id, connections in self.ngo_connections.items():
            if websocket in connections:
                connections.remove(websocket)
                if not connections:  # Clean up empty lists
                    del self.ngo_connections[ngo_id]
                break
                
        print(f"🔌 WebSocket disconnected")

    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"❌ Failed to send to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_to_ngos(self, message: Dict[str, Any], specific_ngo_id: int = None):
        """Broadcast message to NGO clients (all or specific NGO)"""
        message_str = json.dumps(message)
        disconnected = []
        
        if specific_ngo_id and specific_ngo_id in self.ngo_connections:
            # Send to specific NGO
            connections = self.ngo_connections[specific_ngo_id]
            for connection in connections:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    print(f"❌ Failed to send to NGO {specific_ngo_id}: {e}")
                    disconnected.append(connection)
        else:
            # Send to all NGOs
            for ngo_id, connections in self.ngo_connections.items():
                for connection in connections:
                    try:
                        await connection.send_text(message_str)
                    except Exception as e:
                        print(f"❌ Failed to send to NGO {ngo_id}: {e}")
                        disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_to_donors(self, message: Dict[str, Any]):
        """Broadcast message to donor clients"""
        if not self.donor_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.donor_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"❌ Failed to send to donor: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def notify_new_donation(self, donation_data: Dict[str, Any]):
        """Notify all NGOs about a new donation"""
        message = {
            "type": "new_donation",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "id": donation_data.get("id"),
                "restaurant_name": donation_data.get("restaurant_name"),
                "food_description": donation_data.get("food_description"),
                "quantity": donation_data.get("quantity"),
                "latitude": donation_data.get("latitude"),
                "longitude": donation_data.get("longitude"),
                "status": donation_data.get("status", "available"),
                "created_at": donation_data.get("created_at")
            }
        }
        
        await self.broadcast_to_ngos(message)
        print(f"📢 Notified NGOs about new donation: {donation_data.get('restaurant_name')}")

    async def notify_donation_accepted(self, donation_id: int, ngo_id: int, ngo_name: str):
        """Notify about donation acceptance"""
        message = {
            "type": "donation_accepted",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "donation_id": donation_id,
                "ngo_id": ngo_id,
                "ngo_name": ngo_name,
                "status": "accepted"
            }
        }
        
        # Notify all clients about status change
        await self.broadcast_to_all(message)
        print(f"📢 Notified about donation {donation_id} accepted by {ngo_name}")

    async def notify_status_update(self, donation_id: int, old_status: str, new_status: str, ngo_name: str = None):
        """Notify about donation status changes"""
        message = {
            "type": "status_update",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "donation_id": donation_id,
                "old_status": old_status,
                "new_status": new_status,
                "ngo_name": ngo_name
            }
        }
        
        await self.broadcast_to_all(message)
        print(f"📢 Status update: Donation {donation_id} {old_status} → {new_status}")

    async def notify_pickup_update(self, pickup_data: Dict[str, Any]):
        """Notify about pickup progress updates"""
        message = {
            "type": "pickup_update",
            "timestamp": datetime.now().isoformat(),
            "data": pickup_data
        }
        
        await self.broadcast_to_all(message)
        print(f"📢 Pickup update for donation {pickup_data.get('donation_id')}")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections"""
        return {
            "total_connections": len(self.active_connections),
            "ngo_connections": len(self.ngo_connections),
            "donor_connections": len(self.donor_connections),
            "connected_ngos": list(self.ngo_connections.keys())
        }

# Global WebSocket manager instance
websocket_manager = FoodRescueConnectionManager()