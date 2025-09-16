#!/usr/bin/env python3
"""
Automated Data Generator for Food Rescue System
Generates realistic test data for donations and NGOs to test ML allocation
"""

import requests
import random
import json
import time
from datetime import datetime, timedelta

# Configuration
API_BASE = "http://localhost:8000"
DONATION_ENDPOINT = f"{API_BASE}/api/donations/"
NGO_ENDPOINT = f"{API_BASE}/api/ngos/"

def generate_fake_donations(n=5):
    """Generate fake donations compatible with the system schema"""
    food_types = [
        "Fresh Produce",
        "Dairy Products", 
        "Bakery Items",
        "Meat & Seafood",
        "Prepared Meals",
        "Canned Goods",
        "Frozen Foods",
        "Beverages",
        "Other"
    ]
    
    restaurant_names = [
        "Golden Palace Restaurant",
        "Fresh Bites Cafe",
        "Metro Food Court",
        "Sunrise Bakery",
        "Ocean View Seafood",
        "Garden Fresh Market",
        "City Center Deli",
        "Heritage Hotel Kitchen",
        "Corner Street Eatery",
        "Royal Feast Restaurant"
    ]
    
    food_descriptions = {
        "Fresh Produce": ["Mixed vegetables", "Seasonal fruits", "Organic greens", "Root vegetables"],
        "Dairy Products": ["Fresh milk", "Cheese varieties", "Yogurt cups", "Butter packets"],
        "Bakery Items": ["Fresh bread", "Pastries", "Cookies", "Cakes"],
        "Meat & Seafood": ["Grilled chicken", "Fresh fish", "Meat portions", "Seafood platter"],
        "Prepared Meals": ["Ready meals", "Lunch boxes", "Dinner portions", "Buffet leftovers"],
        "Canned Goods": ["Canned vegetables", "Soup cans", "Preserved fruits", "Sauce jars"],
        "Frozen Foods": ["Frozen vegetables", "Ice cream", "Frozen meals", "Meat portions"],
        "Beverages": ["Fruit juices", "Soft drinks", "Water bottles", "Tea/Coffee"],
        "Other": ["Snacks", "Condiments", "Spices", "Mixed items"]
    }
    
    donor_users = ["chef_maria", "baker_john", "manager_sarah", "owner_raj", "cook_alex"]
    
    donations = []
    for i in range(1, n + 1):
        food_type = random.choice(food_types)
        donation = {
            "restaurant_name": random.choice(restaurant_names),
            "food_type": food_type,
            "food_description": random.choice(food_descriptions[food_type]),
            "quantity": random.randint(50, 300),
            "expiry_hours": random.randint(1, 6),
            "latitude": 12.9600 + random.uniform(-0.05, 0.05),  # Bangalore coordinates with variation
            "longitude": 77.5900 + random.uniform(-0.05, 0.05),
            "pickup_address": f"Street {random.randint(1, 100)}, {random.choice(['Koramangala', 'Indiranagar', 'Whitefield', 'Jayanagar', 'BTM Layout'])}, Bangalore",
            "donor_user": random.choice(donor_users)
        }
        donations.append(donation)
    return donations

def generate_fake_ngos(n=3):
    """Generate fake NGOs compatible with the system schema"""
    ngo_names = [
        "Hope Foundation",
        "Feeding Hands NGO",
        "Care & Share Foundation", 
        "Unity Food Bank",
        "Helping Hearts Organization",
        "Community Kitchen Trust",
        "Meal Bridge Foundation",
        "Food For All Initiative",
        "Compassion Network",
        "Nourish India Foundation"
    ]
    
    food_types_combinations = [
        ["Fresh Produce", "Prepared Meals", "Dairy Products"],
        ["Bakery Items", "Beverages", "Canned Goods"],
        ["Meat & Seafood", "Frozen Foods", "Fresh Produce"],
        ["Prepared Meals", "Bakery Items", "Beverages"],
        ["Fresh Produce", "Dairy Products", "Canned Goods"],
        ["Other", "Prepared Meals", "Fresh Produce"]
    ]
    
    ngos = []
    for i in range(1, n + 1):
        ngo = {
            "name": random.choice(ngo_names),
            "contact_phone": f"+91-{random.randint(8000000000, 9999999999)}",
            "accepted_food_types": json.dumps(random.choice(food_types_combinations)),
            "capacity": random.randint(50, 200),
            "latitude": 12.9600 + random.uniform(-0.08, 0.08),  # Wider spread for NGOs
            "longitude": 77.5900 + random.uniform(-0.08, 0.08),
            "reliability": round(random.uniform(3.5, 5.0), 1),
            "recent_donations": random.randint(0, 15),
            "schedule": json.dumps({
                "monday": "9:00-18:00",
                "tuesday": "9:00-18:00", 
                "wednesday": "9:00-18:00",
                "thursday": "9:00-18:00",
                "friday": "9:00-18:00",
                "saturday": "10:00-16:00",
                "sunday": "closed" if random.choice([True, False]) else "10:00-14:00"
            })
        }
        ngos.append(ngo)
    return ngos

def post_donations(donations):
    """Post donations to the API"""
    success_count = 0
    for i, donation in enumerate(donations, 1):
        try:
            response = requests.post(DONATION_ENDPOINT, json=donation)
            if response.status_code == 200:
                success_count += 1
                result = response.json()
                print(f"✅ Donation {i}: {donation['restaurant_name']} - {donation['food_type']} (ID: {result.get('id', 'Unknown')})")
            else:
                print(f"❌ Donation {i} failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Donation {i} error: {str(e)}")
        time.sleep(0.5)  # Small delay to avoid overwhelming the server
    
    return success_count

def post_ngos(ngos):
    """Post NGOs to the API"""
    success_count = 0
    for i, ngo in enumerate(ngos, 1):
        try:
            response = requests.post(NGO_ENDPOINT, json=ngo)
            if response.status_code == 200:
                success_count += 1
                result = response.json()
                print(f"✅ NGO {i}: {ngo['name']} (ID: {result.get('id', 'Unknown')})")
            else:
                print(f"❌ NGO {i} failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ NGO {i} error: {str(e)}")
        time.sleep(0.5)
    
    return success_count

def test_ml_allocation():
    """Test ML allocation on available donations"""
    try:
        # Get available donations
        response = requests.get(f"{API_BASE}/api/donations/?status=available")
        if response.status_code == 200:
            donations = response.json()
            if donations:
                # Test allocation on the first available donation
                donation_id = donations[0]['id']
                print(f"\n🧠 Testing ML allocation for donation ID: {donation_id}")
                
                allocation_response = requests.post(f"{API_BASE}/api/donations/{donation_id}/allocate")
                if allocation_response.status_code == 200:
                    allocation_result = allocation_response.json()
                    print(f"✅ ML Allocation successful!")
                    print(f"📊 Allocations: {len(allocation_result.get('allocations', []))}")
                    for allocation in allocation_result.get('allocations', []):
                        print(f"   • {allocation['ngo_name']}: {allocation['allocated_quantity']} units (Score: {allocation['priority_score']:.2f})")
                else:
                    print(f"❌ ML Allocation failed: {allocation_response.status_code}")
            else:
                print("⚠️ No available donations found for ML testing")
        else:
            print(f"❌ Failed to fetch donations: {response.status_code}")
    except Exception as e:
        print(f"❌ ML test error: {str(e)}")

def main():
    """Main function to generate and post test data"""
    print("🚀 Automated Data Generator for Food Rescue System")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print("✅ Server is running and accessible")
    except:
        print("❌ Server is not accessible. Make sure run.py is running on localhost:8000")
        return
    
    # Generate and post NGOs first
    print(f"\n📋 Generating 5 NGOs...")
    ngos = generate_fake_ngos(5)
    ngo_success = post_ngos(ngos)
    print(f"✅ Successfully created {ngo_success}/5 NGOs")
    
    # Wait a bit for NGOs to be fully created
    time.sleep(1)
    
    # Generate and post donations
    print(f"\n🍽️ Generating 8 donations...")
    donations = generate_fake_donations(8)
    donation_success = post_donations(donations)
    print(f"✅ Successfully created {donation_success}/8 donations")
    
    # Test ML allocation
    print(f"\n🧠 Testing ML allocation system...")
    time.sleep(2)  # Wait for data to be processed
    test_ml_allocation()
    
    print(f"\n🎉 Data generation complete!")
    print(f"📊 Summary: {ngo_success} NGOs, {donation_success} donations created")
    print(f"🌐 View dashboard: http://localhost:8080")
    print(f"🎛️ View frontend: http://localhost:8000")

if __name__ == "__main__":
    main()