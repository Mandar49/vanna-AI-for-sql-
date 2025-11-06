# train.py
from common import LocalVanna, run_sql

# Instantiate the Vanna class. The new architecture handles configuration internally.
vn = LocalVanna()

# Assign the shared database connection function
vn.run_sql = run_sql

def train_vanna():
    print("Starting Vanna training...")
    # DDL Training
    print("Training on DDLs...")
    tables = ["customers", "employees", "departments", "products", "salesorders", "orderitems"]
    for table in tables:
        ddl = vn.run_sql(f"SHOW CREATE TABLE {table}").iloc[0, 1]
        vn.train(ddl=ddl)
        print(f"  - Trained on table: {table}")

    # Documentation Training
    print("\nTraining on documentation...")
    vn.train(documentation="To find an employee's sales, you must join the employees table with the salesorders table on EmployeeID.")
    print("  - Added business logic documentation.")

    # Question-SQL Pair Training
    print("\nTraining on Question-SQL pairs...")
    vn.train(
        question="What are the top 5 products by sales?",
        sql="SELECT p.ProductName, SUM(oi.Quantity * oi.UnitPrice) AS TotalSales FROM products p JOIN orderitems oi ON p.ProductID = oi.ProductID GROUP BY p.ProductName ORDER BY TotalSales DESC LIMIT 5"
    )
    vn.train(
        question="Who are the top 5 employees by sales?",
        sql="SELECT e.FirstName, e.LastName, SUM(so.TotalAmount) AS TotalSales FROM employees e JOIN salesorders so ON e.EmployeeID = so.EmployeeID GROUP BY e.FirstName, e.LastName ORDER BY TotalSales DESC LIMIT 5"
    )
    vn.train(
        question="What is the total sales for each department?",
        sql="SELECT d.DepartmentName, SUM(so.TotalAmount) AS TotalSales FROM departments d JOIN employees e ON d.DepartmentID = e.DepartmentID JOIN salesorders so ON e.EmployeeID = so.EmployeeID GROUP BY d.DepartmentName ORDER BY TotalSales DESC"
    )
    vn.train(
        question="Who are the top 5 customers by sales?",
        sql="SELECT c.CustomerName, SUM(so.TotalAmount) AS TotalSales FROM customers c JOIN salesorders so ON c.CustomerID = so.CustomerID GROUP BY c.CustomerName ORDER BY TotalSales DESC LIMIT 5"
    )
    vn.train(
        question="What is the total sales for each product category?",
        sql="SELECT p.Category, SUM(oi.Quantity * oi.UnitPrice) AS TotalSales FROM products p JOIN orderitems oi ON p.ProductID = oi.ProductID GROUP BY p.Category ORDER BY TotalSales DESC"
    )
    print("  - Added 5 high-quality Question-SQL pairs.")
    print("\nTraining complete. All training data has been added to the Qdrant vector store.")

if __name__ == '__main__':
    train_vanna()
