import sqlite3

conn = sqlite3.connect('food_rescue.db')
cursor = conn.cursor()

# Test the filtering logic directly on database
print("All donations:")
cursor.execute('SELECT id, restaurant_name, donor_user FROM donations ORDER BY created_at DESC')
all_donations = cursor.fetchall()
for row in all_donations:
    print(f"ID: {row[0]}, Restaurant: {row[1]}, Donor: {row[2]}")

print(f"\nTotal donations: {len(all_donations)}")

print("\nDonations for user 'heramb':")
cursor.execute('SELECT id, restaurant_name, donor_user FROM donations WHERE donor_user = ? ORDER BY created_at DESC', ('heramb',))
heramb_donations = cursor.fetchall()
for row in heramb_donations:
    print(f"ID: {row[0]}, Restaurant: {row[1]}, Donor: {row[2]}")

print(f"\nHeramb donations: {len(heramb_donations)}")

conn.close()