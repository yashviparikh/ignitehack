#!/usr/bin/env python3
"""
Food Rescue Database Viewer
Real-time viewer for the SQLite database with auto-refresh and pretty formatting
"""

import sqlite3
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any

class FoodRescueDBViewer:
    def __init__(self, db_path="food_rescue.db"):
        self.db_path = db_path
        self.last_check = 0
        
    def connect(self):
        """Create database connection"""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            print(f"❌ Database connection error: {e}")
            return None
    
    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all data from a specific table"""
        conn = self.connect()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[columns[i]] = value
                data.append(row_dict)
            
            return data
        except sqlite3.Error as e:
            print(f"❌ Error reading {table_name}: {e}")
            return []
        finally:
            conn.close()
    
    def format_json_field(self, value: str) -> str:
        """Format JSON fields for better readability"""
        if not value:
            return "[]"
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return ", ".join(parsed)
            return str(parsed)
        except:
            return str(value)
    
    def format_datetime(self, dt_str: str) -> str:
        """Format datetime for better readability"""
        if not dt_str:
            return "Not set"
        try:
            # Parse ISO format datetime
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return str(dt_str)
    
    def print_donations_table(self, donations: List[Dict]):
        """Print donations in a formatted table"""
        if not donations:
            print("📝 No donations found")
            return
        
        print(f"\n🍽️  DONATIONS ({len(donations)} total)")
        print("=" * 120)
        print(f"{'ID':<3} {'Restaurant':<20} {'Food Description':<25} {'Qty':<5} {'Status':<12} {'Created':<19} {'Expires':<19}")
        print("-" * 120)
        
        for donation in donations:
            print(f"{donation.get('id', 0):<3} "
                  f"{(donation.get('restaurant_name', '') or 'Unknown')[:19]:<20} "
                  f"{(donation.get('food_description', '') or 'No description')[:24]:<25} "
                  f"{donation.get('quantity', 0):<5} "
                  f"{donation.get('status', 'unknown'):<12} "
                  f"{self.format_datetime(donation.get('created_at', '')):<19} "
                  f"{self.format_datetime(donation.get('expires_at', '')):<19}")
    
    def print_ngos_table(self, ngos: List[Dict]):
        """Print NGOs in a formatted table"""
        if not ngos:
            print("📝 No NGOs found")
            return
        
        print(f"\n🏢 NGOs ({len(ngos)} total)")
        print("=" * 120)
        print(f"{'ID':<3} {'Name':<25} {'Phone':<15} {'Capacity':<8} {'Food Types':<30} {'Schedule':<15}")
        print("-" * 120)
        
        for ngo in ngos:
            food_types = self.format_json_field(ngo.get('accepted_food_types', ''))
            print(f"{ngo.get('id', 0):<3} "
                  f"{(ngo.get('name', '') or 'Unknown')[:24]:<25} "
                  f"{(ngo.get('contact_phone', '') or 'No phone')[:14]:<15} "
                  f"{ngo.get('storage_capacity', 0) or 0:<8} "
                  f"{food_types[:29]:<30} "
                  f"{(ngo.get('operating_schedule', '') or '24/7')[:14]:<15}")
    
    def print_pickups_table(self, pickups: List[Dict]):
        """Print pickups in a formatted table"""
        if not pickups:
            print("📝 No pickups found")
            return
        
        print(f"\n🚚 PICKUPS ({len(pickups)} total)")
        print("=" * 100)
        print(f"{'ID':<3} {'Donation ID':<11} {'NGO ID':<7} {'Pickup Time':<19} {'Delivery Time':<19} {'Beneficiaries':<12}")
        print("-" * 100)
        
        for pickup in pickups:
            print(f"{pickup.get('id', 0):<3} "
                  f"{pickup.get('donation_id', 0):<11} "
                  f"{pickup.get('ngo_id', 0):<7} "
                  f"{self.format_datetime(pickup.get('pickup_time', '')):<19} "
                  f"{self.format_datetime(pickup.get('delivery_time', '')):<19} "
                  f"{pickup.get('beneficiaries_count', 0):<12}")
    
    def print_statistics(self, donations: List[Dict], ngos: List[Dict], pickups: List[Dict]):
        """Print database statistics"""
        total_donations = len(donations)
        available_donations = len([d for d in donations if d.get('status') == 'available'])
        delivered_donations = len([d for d in donations if d.get('status') == 'delivered'])
        total_ngos = len(ngos)
        total_pickups = len(pickups)
        total_beneficiaries = sum(p.get('beneficiaries_count', 0) or 0 for p in pickups)
        
        print(f"\n📊 DATABASE STATISTICS")
        print("=" * 50)
        print(f"📦 Total Donations: {total_donations}")
        print(f"   • Available: {available_donations}")
        print(f"   • Delivered: {delivered_donations}")
        print(f"🏢 Total NGOs: {total_ngos}")
        print(f"🚚 Total Pickups: {total_pickups}")
        print(f"👥 Total Beneficiaries Served: {total_beneficiaries}")
    
    def get_db_modification_time(self) -> float:
        """Get database file modification time"""
        try:
            return os.path.getmtime(self.db_path)
        except:
            return 0
    
    def view_database(self, auto_refresh=False, refresh_interval=5):
        """View database contents with optional auto-refresh"""
        print("🔍 Food Rescue Database Viewer")
        print("=" * 50)
        
        if auto_refresh:
            print(f"🔄 Auto-refresh enabled (every {refresh_interval} seconds)")
            print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Clear screen for auto-refresh
                if auto_refresh:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("🔍 Food Rescue Database Viewer (Auto-refresh)")
                    print("=" * 50)
                    print(f"⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Check if database file exists
                if not os.path.exists(self.db_path):
                    print(f"❌ Database file not found: {self.db_path}")
                    if not auto_refresh:
                        break
                    time.sleep(refresh_interval)
                    continue
                
                # Get data from all tables
                donations = self.get_table_data('donations')
                ngos = self.get_table_data('ngos')
                pickups = self.get_table_data('pickups')
                
                # Print all data
                self.print_statistics(donations, ngos, pickups)
                self.print_donations_table(donations)
                self.print_ngos_table(ngos)
                self.print_pickups_table(pickups)
                
                if not auto_refresh:
                    break
                
                print(f"\n🔄 Refreshing in {refresh_interval} seconds... (Ctrl+C to stop)")
                time.sleep(refresh_interval)
                
        except KeyboardInterrupt:
            if auto_refresh:
                print("\n\n⏹️  Auto-refresh stopped by user")
            else:
                print("\n\n👋 Exiting...")
    
    def export_to_json(self, output_file="database_export.json"):
        """Export all data to JSON file"""
        data = {
            "export_time": datetime.now().isoformat(),
            "donations": self.get_table_data('donations'),
            "ngos": self.get_table_data('ngos'),
            "pickups": self.get_table_data('pickups')
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"✅ Database exported to {output_file}")
        except Exception as e:
            print(f"❌ Export failed: {e}")

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Food Rescue Database Viewer")
    parser.add_argument("--db", default="food_rescue.db", help="Database file path")
    parser.add_argument("--auto-refresh", action="store_true", help="Enable auto-refresh")
    parser.add_argument("--interval", type=int, default=5, help="Refresh interval in seconds")
    parser.add_argument("--export", help="Export to JSON file")
    
    args = parser.parse_args()
    
    viewer = FoodRescueDBViewer(args.db)
    
    if args.export:
        viewer.export_to_json(args.export)
    else:
        viewer.view_database(args.auto_refresh, args.interval)

if __name__ == "__main__":
    main()