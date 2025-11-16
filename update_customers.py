import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='ad_ai_testdb'
)

cursor = conn.cursor()

# Update cities based on address
cursor.execute("UPDATE customers SET City='Mumbai' WHERE Address LIKE '%Mumbai%'")
print(f"✓ Updated {cursor.rowcount} customers with City=Mumbai")

cursor.execute("UPDATE customers SET City='Pune' WHERE Address LIKE '%Pune%'")
print(f"✓ Updated {cursor.rowcount} customers with City=Pune")

cursor.execute("UPDATE customers SET City='Nashik' WHERE Address LIKE '%Nashik%'")
print(f"✓ Updated {cursor.rowcount} customers with City=Nashik")

cursor.execute("UPDATE customers SET City='Delhi' WHERE Address LIKE '%Delhi%'")
print(f"✓ Updated {cursor.rowcount} customers with City=Delhi")

# Assign HR manager to selected clients
cursor.execute("""
UPDATE customers 
SET ManagerID = (SELECT EmployeeID FROM employees WHERE FirstName='Ritika' AND LastName='Joshi')
WHERE Industry IN ('Manufacturing','Textiles','Infrastructure')
""")
print(f"✓ Assigned Ritika Joshi as manager to {cursor.rowcount} customers")

conn.commit()
conn.close()
print("\n✅ Customer city and manager mappings updated!")
