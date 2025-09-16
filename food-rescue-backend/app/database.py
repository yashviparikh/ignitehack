from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# SQLite database URL
DATABASE_URL = "sqlite:///./food_rescue.db"

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class Donation(Base):
    __tablename__ = "donations"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String(100), nullable=False)
    food_description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    photo_url = Column(String(255))
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(20), default="available")  # available, accepted, picked_up, delivered
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationship
    pickups = relationship("Pickup", back_populates="donation")

class NGO(Base):
    __tablename__ = "ngos"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_phone = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationship
    pickups = relationship("Pickup", back_populates="ngo")

class Pickup(Base):
    __tablename__ = "pickups"
    
    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey("donations.id"))
    ngo_id = Column(Integer, ForeignKey("ngos.id"))
    pickup_time = Column(DateTime)
    delivery_time = Column(DateTime)
    beneficiaries_count = Column(Integer, default=0)
    
    # Relationships
    donation = relationship("Donation", back_populates="pickups")
    ngo = relationship("NGO", back_populates="pickups")

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()