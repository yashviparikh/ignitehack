#!/usr/bin/env python3
"""
API Test Script for ML Allocation Endpoint
Tests the /donations/{donation_id}/allocate endpoint
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:8000"
ALLOCATION_ENDPOINT = f"{BASE_URL}/donations/{{donation_id}}/allocate"

def test_api_health():
    """Test if the API is running"""
    print("🏥 Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ API is running successfully!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Error during health check: {e}")
        return False

def create_test_donation():
    """Create a test donation"""
    print("\n📦 Creating test donation...")
    
    donation_data = {
        "restaurant_name": "Test Restaurant",
        "food_description": "Bakery Items",
        "quantity": 25,
        "latitude": 12.9716,
        "longitude": 77.5946,
        "expires_at": "2025-09-17T18:00:00"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/donations/", json=donation_data)
        if response.status_code == 200:
            donation = response.json()
            print(f"✅ Donation created successfully!")
            print(f"   Donation ID: {donation['id']}")
            print(f"   Restaurant: {donation['restaurant_name']}")
            print(f"   Food: {donation['food_description']}")
            print(f"   Quantity: {donation['quantity']}")
            return donation['id']
        else:
            print(f"❌ Failed to create donation: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating donation: {e}")
        return None

def create_test_ngos():
    """Create test NGOs"""
    print("\n🏢 Creating test NGOs...")
    
    ngos_data = [
        {
            "name": "Food Bank Central",
            "contact_phone": "+91-9876543210",
            "latitude": 12.977980260385616,
            "longitude": 77.5934550337575,
            "accepted_food_types": json.dumps(["Dairy Products", "Frozen Foods", "Bakery Items"]),
            "storage_capacity": 100,
            "operating_schedule": "24/7"
        },
        {
            "name": "Community Kitchen",
            "contact_phone": "+91-9876543211",
            "latitude": 12.989101732483828,
            "longitude": 77.59770279299,
            "accepted_food_types": json.dumps(["Bakery Items", "Prepared Meals", "Meat & Seafood"]),
            "storage_capacity": 150,
            "operating_schedule": "6AM-10PM"
        },
        {
            "name": "Shelter Care",
            "contact_phone": "+91-9876543212",
            "latitude": 12.98826261834225,
            "longitude": 77.61572224159502,
            "accepted_food_types": json.dumps(["Beverages", "Bakery Items", "Canned Goods"]),
            "storage_capacity": 75,
            "operating_schedule": "24/7"
        }
    ]
    
    created_ngos = []
    for i, ngo_data in enumerate(ngos_data, 1):
        try:
            response = requests.post(f"{BASE_URL}/ngos/", json=ngo_data)
            if response.status_code == 200:
                ngo = response.json()
                print(f"✅ NGO {i} created: {ngo['name']} (ID: {ngo['id']})")
                created_ngos.append(ngo['id'])
            else:
                print(f"❌ Failed to create NGO {i}: {response.status_code}")
        except Exception as e:
            print(f"❌ Error creating NGO {i}: {e}")
    
    print(f"📋 Created {len(created_ngos)} NGOs successfully")
    return created_ngos

def test_allocation_endpoint(donation_id):
    """Test the allocation endpoint"""
    print(f"\n🎯 Testing allocation for donation ID: {donation_id}")
    print("=" * 50)
    
    try:
        url = ALLOCATION_ENDPOINT.format(donation_id=donation_id)
        print(f"📡 Calling: POST {url}")
        
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Allocation successful!")
            print(f"📋 Response:")
            print(json.dumps(result, indent=2))
            
            # Analyze the results
            print(f"\n📊 Analysis:")
            print(f"   Donation ID: {result.get('donation_id')}")
            print(f"   Total Allocations: {len(result.get('allocations', []))}")
            print(f"   Remaining Quantity: {result.get('remaining_quantity')}")
            
            if result.get('allocations'):
                print(f"\n🏆 Top Allocation:")
                top_allocation = result['allocations'][0]
                print(f"   NGO: {top_allocation.get('ngo_name')} (ID: {top_allocation.get('ngo_id')})")
                print(f"   Allocated: {top_allocation.get('allocated_quantity')} units")
                print(f"   Priority Score: {top_allocation.get('priority_score')}")
                print(f"   Distance: {top_allocation.get('distance_km')} km")
                print(f"   Reliability: {top_allocation.get('reliability')}")
            
            return True
            
        else:
            print(f"❌ Allocation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during allocation test: {e}")
        return False

def test_invalid_donation():
    """Test allocation with invalid donation ID"""
    print(f"\n🚫 Testing allocation with invalid donation ID...")
    
    try:
        url = ALLOCATION_ENDPOINT.format(donation_id=99999)
        response = requests.post(url)
        
        if response.status_code == 404:
            print("✅ Correctly returned 404 for invalid donation")
            return True
        else:
            print(f"❌ Expected 404 but got: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error during invalid donation test: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ML Allocation API Test Suite")
    print("=" * 50)
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print()
    
    # Wait a moment for user to start server
    input("Press Enter when the server is ready...")
    print()
    
    # Test 1: API Health
    health_ok = test_api_health()
    if not health_ok:
        print("❌ Cannot proceed - API is not responding")
        return
    
    # Test 2: Create test data
    ngo_ids = create_test_ngos()
    donation_id = create_test_donation()
    
    if not donation_id:
        print("❌ Cannot proceed - failed to create test donation")
        return
    
    # Wait for database to settle
    time.sleep(1)
    
    # Test 3: Valid allocation
    allocation_ok = test_allocation_endpoint(donation_id)
    
    # Test 4: Invalid donation
    invalid_ok = test_invalid_donation()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"API Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Data Creation: {'✅ PASS' if ngo_ids and donation_id else '❌ FAIL'}")
    print(f"Valid Allocation: {'✅ PASS' if allocation_ok else '❌ FAIL'}")
    print(f"Invalid Donation: {'✅ PASS' if invalid_ok else '❌ FAIL'}")
    print()
    
    if health_ok and allocation_ok and invalid_ok:
        print("🎉 ALL API TESTS PASSED!")
        print("💡 Your ML allocation endpoint is working perfectly!")
        print()
        print("🔗 You can now use the endpoint:")
        print(f"   POST {BASE_URL}/donations/{{donation_id}}/allocate")
    else:
        print("⚠️  Some tests failed - check the errors above")

if __name__ == "__main__":
    main()