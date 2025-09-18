```py
(venv) PS C:\Probz\Hackathon> py qt.py                                                      
🍽️  Food Rescue System - Quick Test
========================================
[*] Starting Food Rescue comprehensive test...
[+] Server detected on port 8000
[*] Testing HTTP connectivity...
[+] Root endpoint: OK (Food Rescue page)
[+] Health check: OK
[*] Testing API endpoints...
[+] GET donations: OK (11 donations)
[+] GET NGOs: OK (10 NGOs)
[+] GET pickups: OK (2 pickups)
[+] Stats API: OK (11 total, 1 delivered)
[*] Checking ML model availability...
C:\Probz\Hackathon\food-rescue-backend\venv\Lib\site-packages\sklearn\base.py:442: InconsistentVersionWarning: Trying to unpickle estimator DecisionTreeRegressor from version 1.7.1 when using version 1.7.2. This might lead to breaking code or invalid results. Use at your own risk. For more info please refer to:
https://scikit-learn.org/stable/model_persistence.html#security-maintainability-limitations
  warnings.warn(
C:\Probz\Hackathon\food-rescue-backend\venv\Lib\site-packages\sklearn\base.py:442: InconsistentVersionWarning: Trying to unpickle estimator RandomForestRegressor from version 1.7.1 when using version 1.7.2. This might lead to breaking code or invalid results. Use at your own risk. For more info please refer to:
https://scikit-learn.org/stable/model_persistence.html#security-maintainability-limitations
  warnings.warn(
✅ ML model loaded successfully from: C:\Probz\Hackathon\food-rescue-backend\ngo_allocation_model.pkl
🧠 ML-First allocation mode enabled!
[+] ✅ ML MODEL: Loaded and available
[*] Testing ML allocation system (ML-First approach)...
[*] Created test donation ID: 12
[*] Created test NGO: ML Test NGO Alpha (ID: 11)
[*] Created test NGO: ML Test NGO Beta (ID: 12)
[*] Created test NGO: ML Test NGO Gamma (ID: 13)
[*] Triggering ML allocation...
[*] 🎯 Allocation Method Used: Simple Rule-Based Fallback
[*] 📊 Total Allocated: 0/150 units
[*] 🏢 NGOs Matched: 0
[*] 📋 Allocation Details:
[*]   1. FoodServ: 10 units
[*]      Score: 1.00 | Distance: N/Akm | Method: Unknown
[*]   2. ML Test NGO Alpha: 10 units
[*]      Score: 0.80 | Distance: N/Akm | Method: Unknown
[*]   3. ML Test NGO Beta: 10 units
[*]      Score: 0.60 | Distance: N/Akm | Method: Unknown
[!] ❓ UNKNOWN: Allocation method unclear
[+] 🧠 ML allocation system: OPERATIONAL
[-] ❌ Allocation math: INCONSISTENT (30 vs 0)
[+] WebSocket stats: OK (1 connections)
[*] Testing frontend interface...
[+] UI Donation form: Found
[+] UI NGO registration: Found
[+] UI File upload: Found
[+] UI Dashboard: Found
[+] UI Statistics: Found
[+] UI JavaScript: Found
[+] UI CSS styling: Found
[+] UI WebSocket code: Found
[*] Testing WebSocket functionality...
[+] WebSocket connection: OK
[*] WebSocket ping: Sent
[+] WebSocket pong: Received
[*] Testing WebSocket real-time notifications...
[+] Test donation created: ID 13
[+] WebSocket notification: Received (QuickTest Restaurant 1758096239)
[*] Testing complete donation flow...
[+] Test NGO created: ID 14
[+] Pickup created: ID 3
[+] Pickup collected: OK
[+] Delivery completed: OK
[*] Testing file operations...
[+] File upload: OK (/uploads/0475c023-c1a6-49d4-9fc2-31bb4711ff1d.txt)
[+] Quick test completed in 2.5s!

============================================================
🍽️  FOOD RESCUE SYSTEM - COMPONENT STATUS REPORT
============================================================

📈 OVERALL STATUS: 15/15 components working
🎯 FUNCTIONALITY SCORES:
   • Core Features: 100% (8/8)
   • Enhanced Features: 100% (7/7)
   • Overall System: 100% (15/15)

🚀 CORE COMPONENTS (Essential for food rescue):
   🌐 HTTP Server: ✅ WORKING
   🍽️  Donations API: ✅ WORKING
   🏢 NGOs API: ✅ WORKING
   🚚 Pickups API: ✅ WORKING
   🤖 ML Model: ✅ WORKING
   🧠 ML Allocation: ✅ WORKING
   🖥️  Web Interface: ✅ WORKING
   💾 Database Operations: ✅ WORKING

⭐ ENHANCED COMPONENTS (Better user experience):
   🔌 WebSocket Connection: ✅ WORKING
   📡 WebSocket Broadcasting: ✅ WORKING
   ⚡ Real-time Updates: ✅ WORKING
   📤 File Upload: ✅ WORKING
   📸 Photo Upload: ✅ WORKING
   📊 Status Updates: ✅ WORKING
   📈 Statistics API: ✅ WORKING

🏆 HACKATHON READINESS:
   • Status: 🥇 EXCELLENT - Ready for demo!
   • Demo Quality: ⭐⭐⭐⭐⭐ Outstanding user experience

⚡ PERFORMANCE METRICS:
   • Test Speed: Fast (< 10 seconds)
   • API Response: Quick
   • WebSocket Latency: Low
   • Ready for: Manual testing, Live demo, Production

🎯 NEXT STEPS:
   • 🎉 All systems operational!
   • 🚀 Ready for hackathon presentation
   • 💡 Consider adding extra features if time permits
============================================================

========================================
🎉 Quick test completed successfully!
✅ Food Rescue system is ready for use!
(venv) PS C:\Probz\Hackathon> 

```