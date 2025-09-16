from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3
import shutil
import os
import uuid

# Create FastAPI app
app = FastAPI(title="Food Rescue Matchmaker API", version="1.0.0")

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

# Database setup
def init_db():
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_name TEXT NOT NULL,
            food_description TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            photo_url TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ngos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_phone TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    
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

# Pydantic models
class DonationCreate(BaseModel):
    restaurant_name: str
    food_description: str
    quantity: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class NGOCreate(BaseModel):
    name: str
    contact_phone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PickupCreate(BaseModel):
    donation_id: int
    ngo_id: int

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Food Rescue Matchmaker API is running!", "status": "success"}

@app.post("/donations/")
def create_donation(donation: DonationCreate):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO donations (restaurant_name, food_description, quantity, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
    ''', (donation.restaurant_name, donation.food_description, donation.quantity, 
          donation.latitude, donation.longitude))
    
    donation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": donation_id, "message": "Donation created successfully"}

@app.get("/donations/")
def get_donations(status: Optional[str] = None):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    if status:
        cursor.execute('SELECT * FROM donations WHERE status = ? ORDER BY created_at DESC', (status,))
    else:
        cursor.execute('SELECT * FROM donations ORDER BY created_at DESC')
    
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

@app.post("/donations/{donation_id}/upload-photo")
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

@app.post("/ngos/")
def create_ngo(ngo: NGOCreate):
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ngos (name, contact_phone, latitude, longitude)
        VALUES (?, ?, ?, ?)
    ''', (ngo.name, ngo.contact_phone, ngo.latitude, ngo.longitude))
    
    ngo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": ngo_id, "message": "NGO registered successfully"}

@app.get("/ngos/")
def get_ngos():
    conn = sqlite3.connect('food_rescue.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ngos')
    columns = [description[0] for description in cursor.description]
    ngos = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    conn.close()
    return ngos

@app.post("/pickups/")
def create_pickup(pickup: PickupCreate):
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
    
    return {"id": pickup_id, "message": "Pickup created successfully"}

@app.patch("/pickups/{pickup_id}")
def update_pickup(pickup_id: int, status: str, beneficiaries_count: Optional[int] = None):
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
    
    # Update pickup
    if beneficiaries_count is not None:
        cursor.execute('UPDATE pickups SET beneficiaries_count = ? WHERE id = ?', 
                      (beneficiaries_count, pickup_id))
    
    # Update timestamps and donation status
    if status == "picked_up":
        cursor.execute('UPDATE pickups SET pickup_time = CURRENT_TIMESTAMP WHERE id = ?', (pickup_id,))
        cursor.execute('UPDATE donations SET status = ? WHERE id = ?', ('picked_up', donation_id))
    elif status == "delivered":
        cursor.execute('UPDATE pickups SET delivery_time = CURRENT_TIMESTAMP WHERE id = ?', (pickup_id,))
        cursor.execute('UPDATE donations SET status = ? WHERE id = ?', ('delivered', donation_id))
    
    conn.commit()
    conn.close()
    
    return {"message": f"Pickup updated to {status}"}

@app.get("/stats/")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)