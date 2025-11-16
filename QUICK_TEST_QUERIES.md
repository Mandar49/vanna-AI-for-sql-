# Quick Test Queries for SQL Accuracy

Use these queries to verify that the Executive Intelligence Agent returns accurate data from your database.

## Basic Data Verification

### 1. Check Total Orders
**Query:** "How many orders do we have?"

**Expected:** Exact count from database, no fabrication

**Verify:** The number should match `SELECT COUNT(*) FROM salesorders`

---

### 2. List All Customers
**Query:** "Show me all customers"

**Expected:** Actual customer names from database

**Verify:** Names should match `SELECT CustomerName FROM customers`

---

## Year-over-Year Comparisons

### 3. Sales Comparison 2023 vs 2024
**Query:** "What were our total sales in 2024 compared to 2023?"

**Expected Response Format:**
```
✅ SQL Result:
Year  TotalSales
2023  3996499.31
2024  4110315.23

📊 Analysis:
Sales in 2023 were 3996499.31 and in 2024 were 4110315.23.
Sales increased from 2023 to 2024.

💡 All numbers above are from the actual database query results.
```

**Verify:** 
- Raw SQL results shown first
- Exact numbers from database
- No fabricated calculations

---

### 4. Average Order Value Comparison
**Query:** "What was the average order value in 2024 compared to 2023?"

**Expected:** Exact AVG() values from database

**Correct SQL:**
```sql
SELECT 
    YEAR(OrderDate) AS Year,
    AVG(TotalAmount) AS AvgOrderValue
FROM salesorders
WHERE YEAR(OrderDate) IN (2023, 2024)
GROUP BY YEAR(OrderDate)
ORDER BY Year;
```

---

## Top N Queries

### 5. Top Product by Revenue
**Query:** "Which product generated the most revenue overall?"

**Expected:** Actual product name and revenue sum

**Correct SQL:**
```sql
SELECT 
    p.ProductName,
    SUM(oi.Quantity * oi.UnitPrice) AS TotalRevenue
FROM orderitems oi
JOIN products p ON oi.ProductID = p.ProductID
GROUP BY p.ProductName
ORDER BY TotalRevenue DESC
LIMIT 1;
```

---

### 6. Top Sales Representative
**Query:** "Which sales representative closed the highest number of deals in 2024?"

**Expected:** Actual employee name and deal count

**Correct SQL:**
```sql
SELECT 
    e.FirstName,
    e.LastName,
    COUNT(so.OrderID) AS DealsCount
FROM salesorders so
JOIN employees e ON so.EmployeeID = e.EmployeeID
WHERE YEAR(so.OrderDate) = 2024
GROUP BY e.EmployeeID, e.FirstName, e.LastName
ORDER BY DealsCount DESC
LIMIT 1;
```

---

### 7. Top 3 Customers by Revenue
**Query:** "Who were our top 3 customers by revenue in 2024?"

**Expected:** Actual customer names and revenue totals

**Correct SQL:**
```sql
SELECT 
    c.CustomerName,
    SUM(so.TotalAmount) AS TotalRevenue
FROM salesorders so
JOIN customers c ON so.CustomerID = c.CustomerID
WHERE YEAR(so.OrderDate) = 2024
GROUP BY c.CustomerID, c.CustomerName
ORDER BY TotalRevenue DESC
LIMIT 3;
```

---

## Empty Result Handling

### 8. Query for Non-Existent Data
**Query:** "What were our sales in 2025?"

**Expected Response:**
```
❌ No data found

The query executed successfully but returned no results.

**Possible reasons:**
- The database doesn't contain data matching your criteria
- The date range or filters are too restrictive
- The tables may need to be populated with sample data

💡 Try: 'Show me all customers' or 'List all orders' to verify data exists.
```

**Verify:** No fabricated numbers, clear "no data" message

---

## Error Handling

### 9. Invalid SQL Syntax
If the AI generates invalid SQL (rare), you should see:

```
❌ SQL Execution Failed

[ERROR] SQL Syntax Error (1064): You have an error in your SQL syntax...

**SQL Query:**
[The problematic SQL]

💡 Try rephrasing your question or ask: 'What tables are available?'
```

---

## What to Look For

### ✅ Good Response Indicators:
1. **Raw SQL results shown first** in a code block
2. **Exact numbers** from database (no rounding unless in SQL)
3. **Analysis section** that references the raw data
4. **SQL query displayed** for transparency
5. **Verification note**: "All numbers above are from actual database query results"

### ❌ Bad Response Indicators:
1. Numbers that don't appear in raw SQL results
2. Calculated values not in the query (e.g., growth percentages not in SQL)
3. Assumed or guessed data
4. No raw SQL results shown
5. Generic responses without specific numbers

---

## Testing Checklist

Run these queries and verify:

- [ ] Query 1: Total orders count is exact
- [ ] Query 2: Customer names are real
- [ ] Query 3: 2023 vs 2024 sales use actual data
- [ ] Query 4: Average order values are exact
- [ ] Query 5: Top product is real with actual revenue
- [ ] Query 6: Top sales rep is real with actual count
- [ ] Query 7: Top 3 customers are real with actual revenue
- [ ] Query 8: Non-existent data returns "no data" message
- [ ] All responses show raw SQL results first
- [ ] All responses include SQL query for transparency

---

## Automated Testing

Run the comprehensive test suite:

```bash
python test_sql_accuracy.py
```

This will automatically verify:
- Empty result handling
- Single value accuracy
- Year-over-year comparisons
- Top N queries
- SQL syntax error detection
- Data validation

---

## Database Schema

### Available Tables:
- `customers` - Customer information
- `employees` - Employee records
- `salesorders` - Sales order headers
- `orderitems` - Order line items
- `products` - Product catalog
- `categories` - Product categories
- `contacts` - Contact information
- `leads` - Sales leads
- `departments` - Department structure
- `regions` - Geographic regions

### Key Relationships:
- `salesorders.CustomerID` → `customers.CustomerID`
- `salesorders.EmployeeID` → `employees.EmployeeID`
- `orderitems.OrderID` → `salesorders.OrderID`
- `orderitems.ProductID` → `products.ProductID`
- `products.CategoryID` → `categories.CategoryID`

---

## Troubleshooting

### If you see fabricated numbers:
1. Check if raw SQL results are shown first
2. Verify numbers against the raw results
3. Look for the validation warning: "⚠️ Data Validation Warning"
4. Report the issue with the specific query

### If you get "no data" but expect results:
1. Verify data exists: "Show me all orders"
2. Check date ranges: "What years do we have data for?"
3. Verify table contents: "How many customers do we have?"

### If SQL syntax errors occur:
1. Try rephrasing your question
2. Use simpler queries first
3. Ask: "What tables are available?"
4. Check the SQL query shown in the error message

---

## Support

For issues or questions about SQL accuracy:
1. Review `SQL_ACCURACY_FIX.md` for technical details
2. Run `test_sql_accuracy.py` to verify system health
3. Check the SQL query shown in responses
4. Verify against raw SQL results

**Remember:** All numbers in responses MUST match the raw SQL results shown at the top of each response.
