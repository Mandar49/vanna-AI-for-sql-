import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='ad_ai_testdb'
)

cursor = conn.cursor()

try:
    # Add City column to customers
    cursor.execute("ALTER TABLE customers ADD COLUMN City VARCHAR(100) DEFAULT NULL")
    print("✓ Added City column to customers")
except Exception as e:
    print(f"City column: {e}")

try:
    # Add ManagerID column to customers
    cursor.execute("ALTER TABLE customers ADD COLUMN ManagerID INT(11) DEFAULT NULL")
    print("✓ Added ManagerID column to customers")
except Exception as e:
    print(f"ManagerID column: {e}")

try:
    # Add ShippedDate column to salesorders
    cursor.execute("ALTER TABLE salesorders ADD COLUMN ShippedDate DATE DEFAULT NULL")
    print("✓ Added ShippedDate column to salesorders")
except Exception as e:
    print(f"ShippedDate column: {e}")

try:
    # Add foreign key constraint
    cursor.execute("""ALTER TABLE customers 
                      ADD CONSTRAINT fk_customer_manager 
                      FOREIGN KEY (ManagerID) REFERENCES employees(EmployeeID) 
                      ON DELETE SET NULL""")
    print("✓ Added foreign key constraint fk_customer_manager")
except Exception as e:
    print(f"Foreign key: {e}")

conn.commit()
conn.close()
print("\n✅ Schema updates completed!")
