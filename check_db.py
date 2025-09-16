import sqlite3

conn = sqlite3.connect('food_rescue.db')
cursor = conn.cursor()

# Check table schema
cursor.execute('PRAGMA table_info(donations)')
print('Table schema:')
for row in cursor.fetchall():
    print(row)

# Check sample data
cursor.execute('SELECT id, restaurant_name, food_type, donor_user FROM donations LIMIT 10')
print('\nSample data:')
for row in cursor.fetchall():
    print(row)

conn.close()