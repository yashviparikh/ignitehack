from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from datetime import datetime
import uuid

from .database import get_db, create_tables, Donation, NGO, Pickup
from .schemas import DonationCreate, DonationResponse, NGOCreate, NGOResponse, PickupCreate, PickupUpdate, PickupResponse

# Create FastAPI app
app = FastAPI(title="Food Rescue Matchmaker API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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

# DONATION ENDPOINTS

@app.post("/donations/", response_model=DonationResponse)
def create_donation(donation: DonationCreate, db: Session = Depends(get_db)):
    """Create a new food donation"""
    db_donation = Donation(**donation.dict())
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    return db_donation

@app.get("/donations/", response_model=List[DonationResponse])
def get_donations(status: str = None, db: Session = Depends(get_db)):
    """Get all donations, optionally filter by status"""
    query = db.query(Donation)
    if status:
        query = query.filter(Donation.status == status)
    donations = query.order_by(Donation.created_at.desc()).all()
    return donations

@app.get("/donations/{donation_id}", response_model=DonationResponse)
def get_donation(donation_id: int, db: Session = Depends(get_db)):
    """Get a specific donation"""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    return donation

@app.patch("/donations/{donation_id}/status")
def update_donation_status(donation_id: int, status: str, db: Session = Depends(get_db)):
    """Update donation status"""
    donation = db.query(Donation).filter(Donation.id == donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    
    donation.status = status
    db.commit()
    return {"message": f"Donation status updated to {status}"}

@app.post("/donations/{donation_id}/upload-photo")
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

# NGO ENDPOINTS

@app.post("/ngos/", response_model=NGOResponse)
def create_ngo(ngo: NGOCreate, db: Session = Depends(get_db)):
    """Register a new NGO"""
    db_ngo = NGO(**ngo.dict())
    db.add(db_ngo)
    db.commit()
    db.refresh(db_ngo)
    return db_ngo

@app.get("/ngos/", response_model=List[NGOResponse])
def get_ngos(db: Session = Depends(get_db)):
    """Get all NGOs"""
    return db.query(NGO).all()

# PICKUP ENDPOINTS

@app.post("/pickups/", response_model=PickupResponse)
def create_pickup(pickup: PickupCreate, db: Session = Depends(get_db)):
    """NGO accepts a donation (creates pickup)"""
    # Check if donation exists and is available
    donation = db.query(Donation).filter(Donation.id == pickup.donation_id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    if donation.status != "available":
        raise HTTPException(status_code=400, detail="Donation is not available")
    
    # Create pickup record
    db_pickup = Pickup(**pickup.dict(), pickup_time=datetime.utcnow())
    db.add(db_pickup)
    
    # Update donation status
    donation.status = "accepted"
    
    db.commit()
    db.refresh(db_pickup)
    return db_pickup

@app.patch("/pickups/{pickup_id}")
def update_pickup_status(pickup_id: int, update: PickupUpdate, db: Session = Depends(get_db)):
    """Update pickup status (picked_up, delivered)"""
    pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")
    
    # Update pickup
    if update.beneficiaries_count is not None:
        pickup.beneficiaries_count = update.beneficiaries_count
    
    # Update donation status and pickup timestamps
    donation = pickup.donation
    if update.status == "picked_up":
        donation.status = "picked_up"
        pickup.pickup_time = datetime.utcnow()
    elif update.status == "delivered":
        donation.status = "delivered"
        pickup.delivery_time = datetime.utcnow()
    
    db.commit()
    return {"message": f"Pickup updated to {update.status}"}

@app.get("/pickups/", response_model=List[PickupResponse])
def get_pickups(ngo_id: int = None, db: Session = Depends(get_db)):
    """Get all pickups, optionally filter by NGO"""
    query = db.query(Pickup)
    if ngo_id:
        query = query.filter(Pickup.ngo_id == ngo_id)
    return query.all()

# STATISTICS ENDPOINTS

@app.get("/stats/")
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