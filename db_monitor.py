#!/usr/bin/env python3
"""
Real-time Database Monitor
Simple live view of database changes for testing
"""

import sqlite3
import time
import os
from datetime import datetime

def get_record_counts(db_path="food_rescue.db"):
    """Get quick record counts from all tables"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM donations")
        donations_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ngos")
        ngos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pickups")
        pickups_count = cursor.fetchone()[0]
        
        # Get latest donation
        cursor.execute("SELECT restaurant_name, food_description, status FROM donations ORDER BY id DESC LIMIT 1")
        latest_donation = cursor.fetchone()
        
        conn.close()
        
        return {
            'donations': donations_count,
            'ngos': ngos_count,
            'pickups': pickups_count,
            'latest_donation': latest_donation
        }
    except Exception as e:
        return {'error': str(e)}

def monitor_database():
    """Monitor database changes in real-time"""
    print("🔍 Real-time Database Monitor")
    print("=" * 40)
    print("Watching for changes... (Ctrl+C to stop)\n")
    
    last_counts = None
    
    try:
        while True:
            counts = get_record_counts()
            
            if 'error' in counts:
                print(f"❌ Error: {counts['error']}")
                time.sleep(2)
                continue
            
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Check if counts changed
            if last_counts and counts != last_counts:
                print(f"\n🔔 {current_time} - DATABASE UPDATED!")
                
                if counts['donations'] != last_counts['donations']:
                    print(f"   📦 Donations: {last_counts['donations']} → {counts['donations']}")
                    
                if counts['ngos'] != last_counts['ngos']:
                    print(f"   🏢 NGOs: {last_counts['ngos']} → {counts['ngos']}")
                    
                if counts['pickups'] != last_counts['pickups']:
                    print(f"   🚚 Pickups: {last_counts['pickups']} → {counts['pickups']}")
            
            # Always show current status
            print(f"\r{current_time} | 📦 {counts['donations']} donations | 🏢 {counts['ngos']} NGOs | 🚚 {counts['pickups']} pickups", end="")
            
            if counts['latest_donation']:
                restaurant, food, status = counts['latest_donation']
                print(f" | Latest: {restaurant} - {food} ({status})", end="")
            
            last_counts = counts.copy()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")

if __name__ == "__main__":
    monitor_database()