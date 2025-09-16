from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sqlite3
import shutil
import os
import uuid
import webbrowser
import threading
import time
import json
import asyncio
import socket

# Import ML allocation function from backend
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'food-rescue-backend'))
from app.allocation import get_allocation

# Create FastAPI app
app = FastAPI(title="Food Rescue Matchmaker API", version="1.0.0")

# WebSocket Connection Manager
class FoodRescueConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.ngo_connections: Dict[int, List[WebSocket]] = {}
        self.donor_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket, connection_type: str = "general", ngo_id: int = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if connection_type == "ngo" and ngo_id:
            if ngo_id not in self.ngo_connections:
                self.ngo_connections[ngo_id] = []
            self.ngo_connections[ngo_id].append(websocket)
        elif connection_type == "donor":
            self.donor_connections.append(websocket)
            
        print(f"🔌 WebSocket connected: {connection_type}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.donor_connections:
            self.donor_connections.remove(websocket)
        for ngo_id, connections in list(self.ngo_connections.items()):
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.ngo_connections[ngo_id]
        print(f"🔌 WebSocket disconnected")

    async def broadcast_to_all(self, message: Dict[str, Any]):
        if not self.active_connections:
            return
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

    async def notify_new_donation(self, donation_data: Dict[str, Any]):
        message = {
            "type": "new_donation",
            "timestamp": datetime.now().isoformat(),
            "data": donation_data
        }
        await self.broadcast_to_all(message)
        print(f"📢 Notified about new donation: {donation_data.get('restaurant_name')}")

    async def notify_status_update(self, donation_id: int, old_status: str, new_status: str):
        message = {
            "type": "status_update",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "donation_id": donation_id,
                "old_status": old_status,
                "new_status": new_status
            }
        }
        await self.broadcast_to_all(message)
        print(f"📢 Status update: Donation {donation_id} {old_status} → {new_status}")

    async def notify_ngo_allocation(self, ngo_id: int, allocation_data: Dict[str, Any]):
        """Send allocation notification to specific NGO"""
        if ngo_id in self.ngo_connections:
            message_str = json.dumps(allocation_data)
            disconnected = []
            
            for connection in self.ngo_connections[ngo_id]:
                try:
                    await connection.send_text(message_str)
                except Exception:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.ngo_connections[ngo_id].remove(connection)
                if connection in self.active_connections:
                    self.active_connections.remove(connection)
            
            # Remove empty NGO connection list
            if not self.ngo_connections[ngo_id]:
                del self.ngo_connections[ngo_id]
                
            print(f"📋 Sent allocation notification to NGO {ngo_id} ({len(self.ngo_connections.get(ngo_id, []))} connections)")
        else:
            print(f"⚠️ NGO {ngo_id} not connected via WebSocket")

# Global WebSocket manager
websocket_manager = FoodRescueConnectionManager()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve the frontend
# Mount static files for frontend
app.mount("/food-rescue-frontend", StaticFiles(directory="food-rescue-frontend"), name="frontend")

# Mount uploads directory for serving uploaded images
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Root route serves the main HTML file
@app.get("/")
def serve_frontend():
    return FileResponse("food-rescue-frontend/index.html")

# Database setup
def init_db():
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    # Create tables with new schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_name TEXT NOT NULL,
            food_type TEXT,
            food_description TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiry_hours INTEGER,
            photo_url TEXT,
            latitude REAL,
            longitude REAL,
            pickup_address TEXT,
            status TEXT DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add new columns to existing table if they don't exist
    try:
        cursor.execute('ALTER TABLE donations ADD COLUMN food_type TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE donations ADD COLUMN expiry_hours INTEGER')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE donations ADD COLUMN donor_user TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ngos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_phone TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    
    # Add new NGO fields with database migration
    try:
        cursor.execute('ALTER TABLE ngos ADD COLUMN accepted_food_types TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE ngos ADD COLUMN capacity INTEGER')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE ngos ADD COLUMN reliability REAL')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE ngos ADD COLUMN recent_donations INTEGER')
    except sqlite3.OperationalError:
        pass  # Column already exists
        
    try:
        cursor.execute('ALTER TABLE ngos ADD COLUMN schedule TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pickups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donation_id INTEGER,
            ngo_id INTEGER,
            pickup_time TIMESTAMP,
            delivery_time TIMESTAMP,
            beneficiaries_count INTEGER DEFAULT 0,
            FOREIGN KEY (donation_id) REFERENCES donations(id),
            FOREIGN KEY (ngo_id) REFERENCES ngos(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    # Auto-open browser after a short delay
    def open_browser():
        time.sleep(2)  # Wait for server to start
        # Always open localhost (geolocation works there)
        webbrowser.open("http://localhost:8000")
    
    # Run in a separate thread so it doesn't block startup
    threading.Thread(target=open_browser, daemon=True).start()

# Pydantic models
class DonationCreate(BaseModel):
    restaurant_name: str  # This will serve as donor name
    food_type: Optional[str] = None        # Optional for backward compatibility
    food_description: str # Detailed description  
    quantity: int         # Quantity/servings
    expiry_hours: Optional[int] = None     # Optional for backward compatibility
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pickup_address: Optional[str] = None
    donor_user: Optional[str] = None       # Username of the donor

class NGOCreate(BaseModel):
    name: str
    contact_phone: str
    accepted_food_types: Optional[str] = None  # JSON string of accepted food types
    capacity: Optional[int] = None             # Number of people they can serve
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    reliability: Optional[float] = None        # Rating from 0.0 to 5.0
    recent_donations: Optional[int] = None     # Count of recent donations handled
    schedule: Optional[str] = None             # JSON string of operating schedule

class PickupCreate(BaseModel):
    donation_id: int
    ngo_id: int

# ML Allocation schemas
class AllocationItem(BaseModel):
    ngo_id: int
    ngo_name: str
    allocated_quantity: int
    priority_score: float
    distance_km: Optional[float] = None
    reliability: Optional[float] = 0.8
    capacity: Optional[int] = 100
    allocation_method: Optional[str] = "Unknown"

class AllocationResponse(BaseModel):
    donation_id: int
    allocations: List[AllocationItem]
    remaining_quantity: int
    allocation_method: Optional[str] = "Unknown"
    total_allocated: Optional[int] = 0
    ngos_matched: Optional[int] = 0

# API Endpoints

# Health check - API endpoint
@app.get("/api/health")
def health_check():
    return {"message": "Food Rescue Matchmaker API is running!", "status": "success"}

@app.post("/api/donations/")
async def create_donation(donation: DonationCreate):
    try:
        conn = sqlite3.connect('food_rescue.db')
        cursor = conn.cursor()
        
        # Handle None values for new fields
        food_type = donation.food_type or "Not specified"
        expiry_hours = donation.expiry_hours or 24  # Default to 24 hours
        
        cursor.execute('''
            INSERT INTO donations (restaurant_name, food_type, food_description, quantity, expiry_hours, latitude, longitude, pickup_address, donor_user)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (donation.restaurant_name, food_type, donation.food_description, donation.quantity, 
              expiry_hours, donation.latitude, donation.longitude, donation.pickup_address, donation.donor_user))
        
        donation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Broadcast new donation to all connected clients
        await websocket_manager.notify_new_donation({
            "id": donation_id,
            "restaurant_name": donation.restaurant_name,
            "food_type": food_type,
            "food_description": donation.food_description,
            "quantity": donation.quantity,
            "expiry_hours": expiry_hours,
            "latitude": donation.latitude,
            "longitude": donation.longitude,
            "pickup_address": donation.pickup_address,
            "status": "available",
            "created_at": datetime.now().isoformat()
        })
        
        return {"id": donation_id, "message": "Donation created successfully"}
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/donations/")
def get_donations(status: Optional[str] = None, donor_user: Optional[str] = None):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    query = 'SELECT * FROM donations'
    params = []
    conditions = []
    
    if status:
        conditions.append('status = ?')
        params.append(status)
    
    if donor_user:
        conditions.append('donor_user = ?')
        params.append(donor_user)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY created_at DESC'
    
    cursor.execute(query, params)
    
    columns = [description[0] for description in cursor.description]
    donations = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return donations

@app.patch("/donations/{donation_id}/status")
def update_donation_status(donation_id: int, status: str):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE donations SET status = ? WHERE id = ?', (status, donation_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Donation not found")
    
    conn.commit()
    conn.close()
    
    return {"message": f"Donation status updated to {status}"}

@app.post("/api/donations/{donation_id}/upload-photo")
async def upload_photo(donation_id: int, file: UploadFile = File(...)):
    # Create unique filename
    file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{unique_filename}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update donation with photo URL
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    photo_url = f"/uploads/{unique_filename}"
    cursor.execute('UPDATE donations SET photo_url = ? WHERE id = ?', (photo_url, donation_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Donation not found")
    
    conn.commit()
    conn.close()
    
    return {"photo_url": photo_url}

@app.post("/api/donations/{donation_id}/allocate", response_model=AllocationResponse)
async def allocate_donation(donation_id: int):
    """Allocate a donation to matching NGOs using ML model"""
    try:
        conn = sqlite3.connect('food_rescue.db')
        cursor = conn.cursor()
        
        # 1. Get donation details
        cursor.execute('SELECT * FROM donations WHERE id = ? AND status = "available"', (donation_id,))
        donation_row = cursor.fetchone()
        
        if not donation_row:
            conn.close()
            raise HTTPException(status_code=404, detail="Donation not found or not available")
        
        # 2. Convert to dict (assuming columns: id, restaurant_name, food_type, food_description, quantity, expiry_hours, latitude, longitude, pickup_address, donor_user, status, created_at, photo_url)
        donation_dict = {
            "id": donation_row[0],
            "restaurant_name": donation_row[1],
            "food_type": donation_row[2],
            "food_description": donation_row[3],
            "quantity": donation_row[4],
            "expiry_hours": donation_row[5],
            "latitude": donation_row[6],
            "longitude": donation_row[7],
            "pickup_address": donation_row[8],
            "donor_user": donation_row[9],
            "status": donation_row[10]
        }
        
        # 3. Get all NGOs
        cursor.execute('SELECT * FROM ngos')
        ngo_rows = cursor.fetchall()
        conn.close()
        
        # Convert NGOs to list of dicts (assuming columns: id, name, contact_phone, latitude, longitude, accepted_food_types, capacity, reliability, recent_donations, schedule, created_at)
        ngos_list = []
        for ngo_row in ngo_rows:
            ngos_list.append({
                "id": ngo_row[0],
                "name": ngo_row[1],
                "contact_phone": ngo_row[2],
                "latitude": ngo_row[3],
                "longitude": ngo_row[4],
                "accepted_food_types": ngo_row[5],
                "capacity": ngo_row[6] if ngo_row[6] else 50,  # Default capacity
                "reliability": ngo_row[7] if ngo_row[7] else 3.0,  # Default reliability
                "recent_donations": ngo_row[8] if ngo_row[8] else 0,
                "schedule": ngo_row[9]
            })
        
        # 4. Call ML allocation (fallback to rule-based if import fails)
        try:
            print("🔍 Attempting ML allocation...")
            allocation_result = get_allocation(donation_dict, ngos_list)
            print("✅ ML allocation successful!")
            print(f"🔧 ML allocation result keys: {list(allocation_result.keys())}")
            print("🎉 SYSTEM STATUS: Advanced ML allocation pipeline operational!")
        except Exception as e:
            print(f"❌ ML allocation failed, using simple rule-based allocation: {e}")
            print(f"📊 Error type: {type(e).__name__}")
            print("🔄 FALLBACK ACTIVATED: Using basic rule-based allocation")
            import traceback
            print(f"📋 Full error: {traceback.format_exc()}")
            # Simple rule-based fallback
            allocation_result = {
                "donation_id": donation_id,
                "allocations": [],
                "remaining_quantity": donation_dict["quantity"],
                "allocation_method": "Simple Rule-Based Fallback",
                "total_allocated": 0,
                "ngos_matched": 0
            }
            print("⚠️ SYSTEM STATUS: Using simplified fallback allocation (limited functionality)")
            
            # Allocate to first 3 NGOs if available
            for i, ngo in enumerate(ngos_list[:3]):
                if allocation_result["remaining_quantity"] > 0:
                    allocated = min(10, allocation_result["remaining_quantity"])  # Allocate max 10 per NGO
                    allocation_result["allocations"].append({
                        "ngo_id": ngo["id"],
                        "ngo_name": ngo["name"],
                        "allocated_quantity": allocated,
                        "priority_score": 1.0 - (i * 0.2),  # Decreasing priority
                        "distance_km": None
                    })
                    allocation_result["remaining_quantity"] -= allocated
        
        # 5. Send real-time notifications to matched NGOs
        if allocation_result["allocations"]:
            for allocation in allocation_result["allocations"]:
                ngo_id = allocation["ngo_id"]
                ngo_name = allocation["ngo_name"]
                allocated_quantity = allocation["allocated_quantity"]
                
                # Create notification message for the NGO
                notification_message = {
                    "type": "new_allocation",
                    "timestamp": datetime.now().isoformat(),
                    "data": {
                        "donation_id": donation_id,
                        "donation_title": f"{donation_dict['food_type']} from {donation_dict['restaurant_name']}",
                        "restaurant_name": donation_dict["restaurant_name"],
                        "food_type": donation_dict["food_type"],
                        "food_description": donation_dict["food_description"],
                        "allocated_quantity": allocated_quantity,
                        "total_quantity": donation_dict["quantity"],
                        "expiry_hours": donation_dict["expiry_hours"],
                        "pickup_address": donation_dict["pickup_address"],
                        "priority_score": allocation["priority_score"],
                        "distance_km": allocation.get("distance_km"),
                        "urgent": donation_dict["expiry_hours"] and donation_dict["expiry_hours"] <= 2
                    }
                }
                
                # Send notification to specific NGO
                await websocket_manager.notify_ngo_allocation(ngo_id, notification_message)
                print(f"🔔 Sent allocation notification to NGO {ngo_name} (ID: {ngo_id}) for donation {donation_id}")
        
        return allocation_result
        
    except Exception as e:
        print(f"Error in allocation: {e}")
        raise HTTPException(status_code=500, detail=f"Allocation failed: {str(e)}")

@app.post("/api/ngos/")
def create_ngo(ngo: NGOCreate):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ngos (name, contact_phone, latitude, longitude, accepted_food_types, capacity, reliability, recent_donations, schedule)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ngo.name, ngo.contact_phone, ngo.latitude, ngo.longitude, 
          ngo.accepted_food_types, ngo.capacity, ngo.reliability, ngo.recent_donations, ngo.schedule))
    
    ngo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": ngo_id, "message": "NGO registered successfully"}

@app.get("/api/ngos/")
def get_ngos():
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ngos')
    columns = [description[0] for description in cursor.description]
    ngos = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return ngos

@app.post("/api/pickups/")
async def create_pickup(pickup: PickupCreate):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    # Check if donation exists and is available
    cursor.execute('SELECT status FROM donations WHERE id = ?', (pickup.donation_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="Donation not found")
    
    if result[0] != 'available':
        conn.close()
        raise HTTPException(status_code=400, detail="Donation is not available")
    
    # Create pickup
    cursor.execute('''
        INSERT INTO pickups (donation_id, ngo_id, pickup_time)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (pickup.donation_id, pickup.ngo_id))
    
    # Update donation status
    cursor.execute('UPDATE donations SET status = ? WHERE id = ?', ('accepted', pickup.donation_id))
    
    pickup_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Broadcast status update
    await websocket_manager.notify_status_update(pickup.donation_id, "available", "accepted")
    
    return {"id": pickup_id, "message": "Pickup created successfully"}

@app.patch("/pickups/{pickup_id}")
async def update_pickup(pickup_id: int, status: str, beneficiaries_count: Optional[int] = None):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    # Get pickup and donation info
    cursor.execute('''
        SELECT p.donation_id FROM pickups p WHERE p.id = ?
    ''', (pickup_id,))
    
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="Pickup not found")
    
    donation_id = result[0]
    
    # Get current status for broadcasting
    cursor.execute('SELECT status FROM donations WHERE id = ?', (donation_id,))
    old_status = cursor.fetchone()[0]
    
    # Update pickup
    if beneficiaries_count is not None:
        cursor.execute('UPDATE pickups SET beneficiaries_count = ? WHERE id = ?', 
                      (beneficiaries_count, pickup_id))
    
    # Update timestamps and donation status
    new_status = old_status
    if status == "picked_up":
        cursor.execute('UPDATE pickups SET pickup_time = CURRENT_TIMESTAMP WHERE id = ?', (pickup_id,))
        cursor.execute('UPDATE donations SET status = ? WHERE id = ?', ('picked_up', donation_id))
        new_status = "picked_up"
    elif status == "delivered":
        cursor.execute('UPDATE pickups SET delivery_time = CURRENT_TIMESTAMP WHERE id = ?', (pickup_id,))
        cursor.execute('UPDATE donations SET status = ? WHERE id = ?', ('delivered', donation_id))
        new_status = "delivered"
    
    conn.commit()
    conn.close()
    
    # Broadcast status update if status changed
    if new_status != old_status:
        await websocket_manager.notify_status_update(donation_id, old_status, new_status)
    
    return {"message": f"Pickup updated to {status}"}

@app.get("/api/donations/{donation_id}")
def get_donation(donation_id: int):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, restaurant_name, food_type, food_description, quantity, 
               expiry_hours, photo_url, latitude, longitude, pickup_address, 
               status, created_at
        FROM donations 
        WHERE id = ?
    ''', (donation_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    donation = {
        "id": result[0],
        "restaurant_name": result[1],
        "food_type": result[2],
        "food_description": result[3],
        "quantity": result[4],
        "expiry_hours": result[5],
        "photo_url": result[6],
        "latitude": result[7],
        "longitude": result[8],
        "pickup_address": result[9],
        "status": result[10],
        "created_at": result[11]
    }
    
    return donation

@app.get("/api/pickups/")
def get_pickups():
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, d.restaurant_name, d.food_type, d.quantity, d.pickup_address, n.name as ngo_name
        FROM pickups p
        JOIN donations d ON p.donation_id = d.id
        JOIN ngos n ON p.ngo_id = n.id
        ORDER BY p.pickup_time DESC
    ''')
    
    pickups = []
    for row in cursor.fetchall():
        pickup = {
            "id": row[0],
            "donation_id": row[1],
            "ngo_id": row[2],
            "pickup_time": row[3],
            "delivery_time": row[4],
            "beneficiaries_count": row[5],
            "restaurant_name": row[6],  # Changed from donor_name
            "food_type": row[7],
            "quantity": row[8],
            "pickup_address": row[9],
            "ngo_name": row[10]
        }
        pickups.append(pickup)
    
    conn.close()
    return pickups

@app.get("/api/stats/")
def get_statistics():
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    # Get stats
    cursor.execute('SELECT COUNT(*) FROM donations')
    total_donations = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM donations WHERE status = 'delivered'")
    delivered_donations = cursor.fetchone()[0]
    
    cursor.execute('SELECT COALESCE(SUM(beneficiaries_count), 0) FROM pickups WHERE delivery_time IS NOT NULL')
    total_beneficiaries = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM ngos')
    active_ngos = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_donations": total_donations,
        "delivered_donations": delivered_donations,
        "meals_saved": delivered_donations * 3,
        "total_beneficiaries": total_beneficiaries,
        "active_ngos": active_ngos,
        "waste_prevented_kg": delivered_donations * 2.5
    }

# WEBSOCKET ENDPOINTS

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """General WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, "general")
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Echo back for heartbeat/testing
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.websocket("/ws/ngo/{ngo_id}")
async def ngo_websocket_endpoint(websocket: WebSocket, ngo_id: int):
    """NGO-specific WebSocket endpoint"""
    await websocket_manager.connect(websocket, "ngo", ngo_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.websocket("/ws/donor")
async def donor_websocket_endpoint(websocket: WebSocket):
    """Donor-specific WebSocket endpoint"""
    await websocket_manager.connect(websocket, "donor")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.get("/api/ws/stats")
def get_websocket_stats():
    """Get WebSocket connection statistics"""
    stats = {
        "total_connections": len(websocket_manager.active_connections),
        "ngo_connections": len(websocket_manager.ngo_connections),
        "donor_connections": len(websocket_manager.donor_connections),
        "connected_ngos": list(websocket_manager.ngo_connections.keys())
    }
    return stats

if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Get local IP addresses
    def get_local_ip():
        try:
            # Connect to a remote address to determine the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "Unable to determine"
    
    local_ip = get_local_ip()
    port = 8000
    
    print("\n" + "="*70)
    print("🍽️  FOOD RESCUE MATCHMAKER API SERVER")
    print("="*70)
    print(f"🌐 Server starting on ALL network interfaces (host: 0.0.0.0)")
    print()
    print("📍 RECOMMENDED ACCESS (Geolocation works):")
    print(f"   🏠 http://localhost:{port}")
    print()
    print("🌍 LAN ACCESS (Manual location only):")
    print(f"   📱 Primary LAN: http://{local_ip}:{port}")
    print("   � Alternative IPs:")
    print(f"      • http://192.168.56.1:{port}")
    print(f"      • http://192.168.185.2:{port}")
    print(f"      • http://10.110.8.197:{port}")
    print()
    print("ℹ️  Note: Browser geolocation only works on localhost due to security.")
    print("    LAN users can use manual address entry (works perfectly!).")
    print()
    print("🔗 QUICK LINKS:")
    print(f"   📖 API Docs: http://localhost:{port}/docs")
    print(f"   🎛️  Frontend: http://localhost:{port}")
    print("="*70)
    print("⏹️  Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    # Run server on all interfaces (0.0.0.0) but emphasize localhost
    uvicorn.run(app, host="0.0.0.0", port=port)