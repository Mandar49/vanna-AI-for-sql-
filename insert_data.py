import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='ad_ai_testdb'
)

cursor = conn.cursor()

sql = """INSERT INTO customers (CustomerName, ContactPerson, ContactEmail, PhoneNumber, Address, Industry)
VALUES
('Mehta Infra LLP', 'Priya Sharma', 'priya@mehtainfra.com', '+91-9988776655', 'Pune', 'Infrastructure'),
('Patel Logistics Enterprises', 'Sunil Rao', 'sunil@patellogistics.com', '+91-8877665544', 'Nashik', 'Logistics'),
('Shetty Steel Co.', 'Sneha Iyer', 'sneha@shettysteel.com', '+91-9090909090', 'Mumbai', 'Manufacturing'),
('Deshmukh Textiles Pvt Ltd', 'Tara Reddy', 'tara@deshmukhtextiles.com', '+91-8190979892', 'Delhi', 'Textiles')"""

try:
    cursor.execute(sql)
    conn.commit()
    print(f"✓ Successfully inserted {cursor.rowcount} new customer records")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
