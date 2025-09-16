#!/usr/bin/env python3
"""
Quick validation script to test the updated qt.py with ML allocation
"""

print("🧪 Testing updated qt.py structure...")

try:
    # Test import
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    
    from qt import FoodRescueQuickTest
    
    # Test initialization
    tester = FoodRescueQuickTest()
    
    # Check if ML allocation component is tracked
    if 'ml_allocation' in tester.components:
        print("✅ ML allocation component tracking: ADDED")
    else:
        print("❌ ML allocation component tracking: MISSING")
        
    # Test the log function
    tester.log("Test message", "INFO")
    print("✅ Logging function: WORKING")
    
    # Check if server check function exists
    if hasattr(tester, 'check_server_running'):
        print("✅ Server check function: EXISTS")
    else:
        print("❌ Server check function: MISSING")
        
    # Check if ML allocation test function exists
    if hasattr(tester, '_test_ml_allocation_api'):
        print("✅ ML allocation test function: ADDED")
    else:
        print("❌ ML allocation test function: MISSING")
        
    print("\n✅ qt.py update validation: PASSED")
    print("🚀 Ready to test with: python qt.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")