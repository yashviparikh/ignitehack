from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Donation schemas
class DonationCreate(BaseModel):
    restaurant_name: str
    food_description: str
    quantity: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    expires_at: Optional[datetime] = None

class DonationResponse(BaseModel):
    id: int
    restaurant_name: str
    food_description: str
    quantity: int
    photo_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# NGO schemas
class NGOCreate(BaseModel):
    name: str
    contact_phone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accepted_food_types: Optional[str] = None  # JSON string of food types
    storage_capacity: Optional[int] = None
    operating_schedule: Optional[str] = None

class NGOResponse(BaseModel):
    id: int
    name: str
    contact_phone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accepted_food_types: Optional[str] = None
    storage_capacity: Optional[int] = None
    operating_schedule: Optional[str] = None

    class Config:
        from_attributes = True

# Pickup schemas
class PickupCreate(BaseModel):
    donation_id: int
    ngo_id: int
    beneficiaries_count: Optional[int] = 0

class PickupUpdate(BaseModel):
    status: str  # accepted, picked_up, delivered
    beneficiaries_count: Optional[int] = None

class PickupResponse(BaseModel):
    id: int
    donation_id: int
    ngo_id: int
    pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    beneficiaries_count: int

    class Config:
        from_attributes = True

# ML Allocation schemas
class AllocationItem(BaseModel):
    ngo_id: int
    ngo_name: str
    allocated_quantity: int
    priority_score: float
    distance_km: float
    reliability: float
    capacity: int

class AllocationResponse(BaseModel):
    donation_id: int
    allocations: list[AllocationItem]
    remaining_quantity: int