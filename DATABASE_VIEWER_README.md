# 🔍 Food Rescue Database Viewer Tools

## 📊 What I Created for You

### 1. **`db_viewer.py`** - Complete Database Viewer
**Purpose**: View all database contents in readable format

**Usage:**
```bash
# View database once
python db_viewer.py

# Auto-refresh every 5 seconds
python db_viewer.py --auto-refresh

# Custom refresh interval (10 seconds)
python db_viewer.py --auto-refresh --interval 10

# Export to JSON
python db_viewer.py --export backup.json
```

**Features:**
- ✅ Shows all donations, NGOs, and pickups in formatted tables
- ✅ Database statistics (totals, available, delivered)
- ✅ Auto-refresh mode for real-time monitoring
- ✅ JSON export functionality
- ✅ Handles JSON fields (accepted_food_types)
- ✅ Formats dates properly

### 2. **`db_monitor.py`** - Real-time Monitor
**Purpose**: Live monitoring of database changes

**Usage:**
```bash
python db_monitor.py
```

**Features:**
- ✅ Real-time count updates
- ✅ Change notifications when data is added/modified
- ✅ Shows latest donation info
- ✅ Minimal, fast interface

## 🎯 Current Database Status (from your test):

### 📦 **Donations: 19 total**
- Available: 6
- Delivered: 7  
- Accepted: 6

### 🏢 **NGOs: 22 total**
- Including ML test NGOs
- Various food type acceptance

### 🚚 **Pickups: 13 total**
- Active pickup coordination

## 🧪 Perfect for Testing ML Allocation!

Now when you test your ML allocation endpoint:

1. **Before Testing:**
   ```bash
   python db_viewer.py --auto-refresh
   ```

2. **Test ML Allocation:**
   ```bash
   curl -X POST http://localhost:8000/donations/17/allocate
   ```

3. **Watch Results:**
   - The viewer will show real-time updates
   - You can see new pickups created
   - Status changes are visible immediately

## 🎉 Benefits:

✅ **No more binary SQLite confusion**
✅ **Real-time testing feedback**
✅ **Easy data verification**
✅ **Export capability for analysis**
✅ **Clean, readable format**

Your database is now completely transparent and easy to monitor! 🚀