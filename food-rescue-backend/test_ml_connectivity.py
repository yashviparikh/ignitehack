#!/usr/bin/env python3
"""
Test script for ML allocation connectivity
Tests the allocation system independently before running the full API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.allocation import get_allocation

def test_allocation_connectivity():
    print("🧪 Testing ML Allocation Connectivity...")
    print("=" * 50)
    
    # Test data - matching the format expected by your ML system
    donation = {
        "id": 1,
        "food_type": "Bakery Items",
        "quantity": 17,
        "expiry_hours": 3,
        "lat": 12.9716,
        "lon": 77.5946
    }
    
    ngos = [
        {
            "id": 1,
            "name": "NGO_1",
            "accepted_food_types": ["Dairy Products", "Frozen Foods"],
            "capacity": 96,
            "lat": 12.977980260385616,
            "lon": 77.5934550337575,
            "reliability": 0.84,
            "recent_donations": 3,
            "schedule": "dinner"
        },
        {
            "id": 2,
            "name": "NGO_2",
            "accepted_food_types": ["Bakery Items", "Other", "Meat & Seafood"],
            "capacity": 194,
            "lat": 12.989101732483828,
            "lon": 77.59770279299,
            "reliability": 0.87,
            "recent_donations": 4,
            "schedule": "lunch"
        },
        {
            "id": 3,
            "name": "NGO_3",
            "accepted_food_types": ["Beverages", "Bakery Items"],
            "capacity": 55,
            "lat": 12.98826261834225,
            "lon": 77.61572224159502,
            "reliability": 0.86,
            "recent_donations": 2,
            "schedule": "dinner"
        }
    ]
    
    try:
        print(f"📦 Testing donation: {donation['quantity']} units of {donation['food_type']}")
        print(f"🏢 Testing with {len(ngos)} NGOs")
        print()
        
        # Call the allocation function
        result = get_allocation(donation, ngos)
        
        print("✅ Allocation successful!")
        print(f"📋 Donation ID: {result['donation_id']}")
        print(f"📦 Remaining quantity: {result['remaining_quantity']}")
        print()
        
        if result['allocations']:
            print("🎯 Allocations:")
            for i, allocation in enumerate(result['allocations'], 1):
                print(f"  {i}. NGO: {allocation['ngo_name']} (ID: {allocation['ngo_id']})")
                print(f"     Allocated: {allocation['allocated_quantity']} units")
                print(f"     Priority Score: {allocation['priority_score']}")
                print(f"     Distance: {allocation['distance_km']} km")
                print(f"     Reliability: {allocation['reliability']}")
                print()
        else:
            print("❌ No allocations found - check food type compatibility")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during allocation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_model_loading():
    print("🤖 Testing ML Model Loading...")
    print("=" * 50)
    
    try:
        import joblib
        import os
        
        model_path = os.path.join(os.path.dirname(__file__), "ngo_allocation_model.pkl")
        print(f"📂 Model path: {model_path}")
        print(f"📁 Model exists: {os.path.exists(model_path)}")
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print(f"✅ Model loaded successfully: {type(model)}")
            return True
        else:
            print("❌ Model file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def test_dependencies():
    print("📦 Testing Dependencies...")
    print("=" * 50)
    
    dependencies = ['geopy', 'joblib', 'numpy', 'sklearn']
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} - OK")
        except ImportError:
            print(f"❌ {dep} - MISSING")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🚀 ML Allocation System Test Suite")
    print("=" * 50)
    print()
    
    # Test 1: Dependencies
    deps_ok = test_dependencies()
    print()
    
    # Test 2: ML Model Loading
    model_ok = test_ml_model_loading()
    print()
    
    # Test 3: Allocation Logic
    allocation_ok = test_allocation_connectivity()
    print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Dependencies: {'✅ PASS' if deps_ok else '❌ FAIL'}")
    print(f"ML Model: {'✅ PASS' if model_ok else '❌ FAIL'}")
    print(f"Allocation: {'✅ PASS' if allocation_ok else '❌ FAIL'}")
    print()
    
    if deps_ok and model_ok and allocation_ok:
        print("🎉 ALL TESTS PASSED - ML allocation system is ready!")
        print("💡 You can now test the API endpoint: POST /donations/{id}/allocate")
    else:
        print("⚠️  Some tests failed - check the errors above")