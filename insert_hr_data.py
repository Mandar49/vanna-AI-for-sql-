import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='ad_ai_testdb'
)

cursor = conn.cursor()

# Insert HR department if not exists
cursor.execute("""
INSERT INTO departments (DepartmentName)
SELECT 'HR' WHERE NOT EXISTS (SELECT 1 FROM departments WHERE DepartmentName='HR')
""")
print("✓ HR department added/verified")

# Insert HR employees
cursor.execute("""
INSERT INTO employees (FirstName, LastName, Email, PhoneNumber, HireDate, JobTitle, DepartmentID, Salary, ActiveStatus, Address, DateOfBirth, Role)
VALUES
('Ritika', 'Joshi', 'ritika.joshi@example.com', '+91-9123456789', '2022-06-15', 'HR Manager', 
 (SELECT DepartmentID FROM departments WHERE DepartmentName='HR'), 145000.00, 1, 'Pune', '1990-09-10', 'HR Manager'),
('Arjun', 'Mehta', 'arjun.mehta@example.com', '+91-9876543210', '2023-03-20', 'HR Associate', 
 (SELECT DepartmentID FROM departments WHERE DepartmentName='HR'), 98000.00, 1, 'Nashik', '1996-02-11', 'HR Associate')
""")

conn.commit()
print(f"✓ Inserted {cursor.rowcount} HR employees")

conn.close()
print("\n✅ HR data inserted successfully!")
