import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='ad_ai_testdb'
)

cursor = conn.cursor()
cursor.execute("SELECT ContactPerson, PhoneNumber FROM customers WHERE ContactPerson IN ('Priya Sharma', 'Sunil Rao', 'Sneha Iyer', 'Tara Reddy')")
results = cursor.fetchall()

print("✓ New customers added:")
for r in results:
    print(f"  {r[0]}: {r[1]}")

conn.close()
