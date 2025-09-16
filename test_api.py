import sqlite3
import urllib.request
import json

# Test the API endpoints
def test_api():
    try:
        # Test all donations
        response = urllib.request.urlopen('http://localhost:8000/api/donations/')
        all_donations = json.loads(response.read().decode())
        print(f"All donations: {len(all_donations)}")
        for d in all_donations:
            print(f"  - {d['restaurant_name']} by {d.get('donor_user', 'None')}")
        
        # Test filtered for 'abc'
        response = urllib.request.urlopen('http://localhost:8000/api/donations/?donor_user=abc')
        abc_donations = json.loads(response.read().decode())
        print(f"\nABC donations: {len(abc_donations)}")
        for d in abc_donations:
            print(f"  - {d['restaurant_name']} by {d.get('donor_user', 'None')}")
        
        # Test filtered for 'heramb'
        response = urllib.request.urlopen('http://localhost:8000/api/donations/?donor_user=heramb')
        heramb_donations = json.loads(response.read().decode())
        print(f"\nHeramb donations: {len(heramb_donations)}")
        for d in heramb_donations:
            print(f"  - {d['restaurant_name']} by {d.get('donor_user', 'None')}")
            
    except Exception as e:
        print(f"Error: {e}")

test_api()