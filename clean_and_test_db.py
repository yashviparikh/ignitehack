import sqlite3

conn = sqlite3.connect('food_rescue.db')
cursor = conn.cursor()

# Clear all donations to start fresh
cursor.execute('DELETE FROM donations')

# Insert a test donation for user 'abc'
cursor.execute('''
    INSERT INTO donations (restaurant_name, food_type, food_description, quantity, expiry_hours, donor_user)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('ABC Restaurant', 'Prepared Meals', 'Fresh prepared meals', 50, 24, 'abc'))

# Insert a test donation for user 'heramb'
cursor.execute('''
    INSERT INTO donations (restaurant_name, food_type, food_description, quantity, expiry_hours, donor_user)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('Heramb Cafe', 'Vegetables', 'Fresh vegetables', 30, 48, 'heramb'))

# Insert a test donation for user 'test'
cursor.execute('''
    INSERT INTO donations (restaurant_name, food_type, food_description, quantity, expiry_hours, donor_user)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('Test Restaurant', 'Bakery', 'Fresh bread', 20, 12, 'test'))

conn.commit()

# Verify the data
cursor.execute('SELECT id, restaurant_name, donor_user FROM donations ORDER BY id')
print("Test data inserted:")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, Restaurant: {row[1]}, User: {row[2]}")

conn.close()
print("\nDatabase cleaned and test data inserted successfully!")