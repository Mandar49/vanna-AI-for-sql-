# train.py
from common import vn, AppConfig

def train_vanna():
    """
    This script performs the one-time "Three Pillar" training for the Vanna AI agent.
    It teaches the AI about your database schema, relevant business documentation,
    and advanced analytical query patterns.
    """
    print("Starting Vanna training...")

    # --- Pillar 1: DDL Training ---
    # Teach the AI the structure of your database tables.
    print("Training on DDLs...")
    tables = ["customers", "employees", "departments", "products", "salesorders", "orderitems"]
    for table in tables:
        # Get the CREATE TABLE statement for each table.
        ddl = vn.run_sql(f"SHOW CREATE TABLE {table}").iloc[0, 1]
        # Train the Vanna instance on the DDL.
        vn.train(ddl=ddl)
        print(f"  - Trained on table: {table}")

    # --- Pillar 2: Documentation Training ---
    # Teach the AI important business rules and logic.
    print("\nTraining on documentation...")
    vn.train(documentation="To find an employee's sales, you must join the employees table with the salesorders table on EmployeeID.")
    print("  - Added business logic documentation.")

    # --- Pillar 3: Question-SQL Pair Training ---
    # Teach the AI how to answer complex, multi-join analytical questions.
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
        question="Who are the top 5 customers by total spending?",
        sql="SELECT c.CustomerName, SUM(so.TotalAmount) AS TotalSales FROM customers c JOIN salesorders so ON c.CustomerID = so.CustomerID GROUP BY c.CustomerName ORDER BY TotalSales DESC LIMIT 5"
    )
    vn.train(
        question="What is the total sales for each product category?",
        sql="SELECT p.Category, SUM(oi.Quantity * oi.UnitPrice) AS TotalSales FROM products p JOIN orderitems oi ON p.ProductID = oi.ProductID GROUP BY p.Category ORDER BY TotalSales DESC"
    )
    print("  - Added 5 high-quality Question-SQL pairs.")

    print(f"\nTraining complete. Vector store created at: '{AppConfig.CHROMA_DB_PATH}'")

if __name__ == '__main__':
    train_vanna()
