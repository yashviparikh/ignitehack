from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from datetime import datetime
import uuid
import json

from .database import get_db, create_tables, Donation, NGO, Pickup
from .schemas import DonationCreate, DonationResponse, NGOCreate, NGOResponse, PickupCreate, PickupUpdate, PickupResponse, AllocationResponse
from .websocket_manager import websocket_manager
from .allocation import get_allocation

# Create FastAPI app
app = FastAPI(title="Food Rescue Matchmaker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (uploaded photos)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Health check
@app.get("/")
def read_root():
    return {"message": "Food Rescue Matchmaker API is running!"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "Food Rescue Matchmaker API is running!"}

# DONATION ENDPOINTS

@app.post("/api/donations/", response_model=DonationResponse)
async def create_donation(donation: DonationCreate, db: Session = Depends(get_db)):
    """Create a new food donation"""
    db_donation = Donation(**donation.dict())
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    
    # Convert SQLAlchemy object to dict for WebSocket notification
    donation_data = {
        "id": db_donation.id,
        "restaurant_name": db_donation.restaurant_name,
        "food_description": db_donation.food_description,
        "quantity": db_donation.quantity,
        "latitude": db_donation.latitude,
        "longitude": db_donation.longitude,
        "status": db_donation.status,
        "created_at": db_donation.created_at.isoformat() if db_donation.created_at else None
    }
    
    # Notify all NGOs about new donation via WebSocket
    await websocket_manager.notify_new_donation(donation_data)
    
    return db_donation

@app.get("/api/donations/", response_model=List[DonationResponse])
def get_donations(status: str = None, db: Session = Depends(get_db)):
    """Get all donations, optionally filter by status"""
    query = db.query(Donation)
    if status:
        query = query.filter(Donation.status == status)
    donations = query.order_by(Donation.created_at.desc()).all()
    return donations

@app.get("/api/donations/{donation_id}", response_model=DonationResponse)
def get_donation(donation_id: int, db: Session = Depends(get_db)):
    """Get a specific donation"""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    return donation

@app.patch("/api/donations/{donation_id}/status")
async def update_donation_status(donation_id: int, status: str, db: Session = Depends(get_db)):
    """Update donation status"""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    old_status = donation.status
    donation.status = status
    db.commit()
    
    # Notify all clients about status update via WebSocket
    await websocket_manager.notify_status_update(donation_id, old_status, status)
    
    return {"message": f"Donation status updated to {status}"}

@app.post("/api/donations/{donation_id}/upload-photo")
async def upload_photo(donation_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload photo for a donation"""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    # Create unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{unique_filename}"
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update donation with photo URL
    donation.photo_url = f"/uploads/{unique_filename}"
    db.commit()
    
    return {"photo_url": donation.photo_url}

@app.post("/api/donations/{donation_id}/allocate", response_model=AllocationResponse)
def allocate_donation(donation_id: int, db: Session = Depends(get_db)):
    """Allocate a donation to matching NGOs using ML model"""
    # 1. Fetch donation
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    # 2. Fetch all NGOs
    ngos = db.query(NGO).all()

    # 3. Convert DB objects to dicts (matching your ML input format)
    donation_dict = {
        "id": donation.id,
        "food_type": donation.food_description,  # Using food_description as food_type
        "quantity": donation.quantity,
        "expiry_hours": (donation.expires_at - datetime.utcnow()).total_seconds() // 3600 if donation.expires_at else 24,
        "lat": donation.latitude or 0.0,
        "lon": donation.longitude or 0.0
    }

    ngos_list = []
    for ngo in ngos:
        # Parse accepted_food_types if it's a JSON string
        accepted_types = ngo.accepted_food_types
        if isinstance(accepted_types, str):
            try:
                import json
                accepted_types = json.loads(accepted_types)
            except:
                accepted_types = [accepted_types] if accepted_types else []
        elif accepted_types is None:
            accepted_types = []
        
        ngos_list.append({
            "id": ngo.id,
            "name": ngo.name,
            "accepted_food_types": accepted_types,
            "capacity": ngo.storage_capacity or 100,
            "lat": ngo.latitude or 0.0,
            "lon": ngo.longitude or 0.0,
            "reliability": 0.85,  # Default reliability score
            "recent_donations": 0,  # TODO: Calculate from recent pickups
            "schedule": ngo.operating_schedule or "24/7"
        })

    # 4. Call ML allocation
    allocation_result = get_allocation(donation_dict, ngos_list)
    print(allocation_result)
    # 5. Return result
    return allocation_result
    

# NGO ENDPOINTS

@app.post("/api/ngos/", response_model=NGOResponse)
def create_ngo(ngo: NGOCreate, db: Session = Depends(get_db)):
    """Register a new NGO"""
    import json
    
    # Convert food types list to JSON string if it's a list
    ngo_data = ngo.dict()
    if isinstance(ngo_data.get('accepted_food_types'), list):
        ngo_data['accepted_food_types'] = json.dumps(ngo_data['accepted_food_types'])
    
    db_ngo = NGO(**ngo_data)
    db.add(db_ngo)
    db.commit()
    db.refresh(db_ngo)
    return db_ngo

@app.get("/api/ngos/", response_model=List[NGOResponse])
def get_ngos(db: Session = Depends(get_db)):
    """Get all NGOs"""
    return db.query(NGO).all()

# PICKUP ENDPOINTS

@app.post("/api/pickups/", response_model=PickupResponse)
async def create_pickup(pickup: PickupCreate, db: Session = Depends(get_db)):
    """NGO accepts a donation (creates pickup)"""
    # Check if donation exists and is available
    donation = db.query(Donation).filter(Donation.id == pickup.donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.status != "available":
        raise HTTPException(status_code=400, detail="Donation is not available")
    
    # Get NGO name for notification
    ngo = db.query(NGO).filter(NGO.id == pickup.ngo_id).first()
    ngo_name = ngo.name if ngo else "Unknown NGO"
    
    # Create pickup record
    db_pickup = Pickup(**pickup.dict(), pickup_time=datetime.utcnow())
    db.add(db_pickup)
    
    # Update donation status
    donation.status = "accepted"
    
    db.commit()
    db.refresh(db_pickup)
    
    # Notify all clients about donation acceptance via WebSocket
    await websocket_manager.notify_donation_accepted(pickup.donation_id, pickup.ngo_id, ngo_name)
    
    return db_pickup

@app.patch("/api/pickups/{pickup_id}")
async def update_pickup_status(pickup_id: int, update: PickupUpdate, db: Session = Depends(get_db)):
    """Update pickup status (picked_up, delivered)"""
    pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")
    
    # Get NGO name for notification
    ngo = db.query(NGO).filter(NGO.id == pickup.ngo_id).first()
    ngo_name = ngo.name if ngo else "Unknown NGO"
    
    # Update pickup
    if update.beneficiaries_count is not None:
        pickup.beneficiaries_count = update.beneficiaries_count
    
    # Update donation status and pickup timestamps
    donation = pickup.donation
    old_status = donation.status
    
    if update.status == "picked_up":
        donation.status = "picked_up"
        pickup.pickup_time = datetime.utcnow()
    elif update.status == "delivered":
        donation.status = "delivered"
        pickup.delivery_time = datetime.utcnow()
    
    db.commit()
    
    # Notify all clients about pickup status update via WebSocket
    pickup_data = {
        "pickup_id": pickup_id,
        "donation_id": pickup.donation_id,
        "ngo_id": pickup.ngo_id,
        "ngo_name": ngo_name,
        "status": update.status,
        "beneficiaries_count": pickup.beneficiaries_count
    }
    await websocket_manager.notify_pickup_update(pickup_data)
    await websocket_manager.notify_status_update(pickup.donation_id, old_status, donation.status, ngo_name)
    
    return {"message": f"Pickup updated to {update.status}"}

@app.get("/api/pickups/", response_model=List[PickupResponse])
def get_pickups(ngo_id: int = None, db: Session = Depends(get_db)):
    """Get all pickups, optionally filter by NGO"""
    query = db.query(Pickup)
    if ngo_id:
        query = query.filter(Pickup.ngo_id == ngo_id)
    return query.all()

# STATISTICS ENDPOINTS

@app.get("/api/stats/")
def get_statistics(db: Session = Depends(get_db)):
    """Get platform statistics for impact dashboard"""
    total_donations = db.query(Donation).count()
    delivered_donations = db.query(Donation).filter(Donation.status == "delivered").count()
    total_beneficiaries = db.query(Pickup).filter(Pickup.delivery_time.isnot(None)).with_entities(
        db.func.sum(Pickup.beneficiaries_count)
    ).scalar() or 0
    
    active_ngos = db.query(NGO).count()
    
    return {
        "total_donations": total_donations,
        "delivered_donations": delivered_donations,
        "meals_saved": delivered_donations * 3,  # Estimate 3 meals per donation
        "total_beneficiaries": total_beneficiaries,
        "active_ngos": active_ngos,
        "waste_prevented_kg": delivered_donations * 2.5  # Estimate 2.5kg per donation
    }

# WEBSOCKET ENDPOINTS

@app.websocket("/ws/general")
async def websocket_general_endpoint(websocket: WebSocket):
    """General WebSocket endpoint for all real-time updates"""
    await websocket_manager.connect(websocket, "general")
    try:
        while True:
            # Keep connection alive and listen for client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.websocket("/ws/ngo/{ngo_id}")
async def websocket_ngo_endpoint(websocket: WebSocket, ngo_id: int):
    """NGO-specific WebSocket endpoint for targeted notifications"""
    await websocket_manager.connect(websocket, "ngo", ngo_id)
    try:
        while True:
            # Keep connection alive and listen for client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.websocket("/ws/donor")
async def websocket_donor_endpoint(websocket: WebSocket):
    """Donor-specific WebSocket endpoint for donation status updates"""
    await websocket_manager.connect(websocket, "donor")
    try:
        while True:
            # Keep connection alive and listen for client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

@app.get("/api/websocket/stats")
def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return websocket_manager.get_connection_stats()