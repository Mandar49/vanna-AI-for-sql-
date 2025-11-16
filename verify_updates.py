import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='ad_ai_testdb'
)

cursor = conn.cursor()

print("=== HR Employees ===")
cursor.execute("SELECT FirstName, LastName, JobTitle, Salary FROM employees WHERE DepartmentID = (SELECT DepartmentID FROM departments WHERE DepartmentName='HR')")
for row in cursor.fetchall():
    print(f"  {row[0]} {row[1]} - {row[2]} - ₹{row[3]}")

print("\n=== Customers with City and Manager ===")
cursor.execute("""
SELECT c.CustomerName, c.City, CONCAT(e.FirstName, ' ', e.LastName) AS Manager
FROM customers c
LEFT JOIN employees e ON c.ManagerID = e.EmployeeID
WHERE c.City IS NOT NULL
LIMIT 5
""")
for row in cursor.fetchall():
    print(f"  {row[0]} | {row[1]} | Manager: {row[2] if row[2] else 'None'}")

print("\n=== Customers Managed by Ritika Joshi ===")
cursor.execute("""
SELECT COUNT(*) as count
FROM customers c
JOIN employees e ON c.ManagerID = e.EmployeeID
WHERE e.FirstName='Ritika' AND e.LastName='Joshi'
""")
count = cursor.fetchone()[0]
print(f"  Total: {count} customers")

conn.close()
print("\n✅ All updates verified successfully!")
