"""
Test script for SQL Corrector - Error-tolerant SQL execution
"""
from sql_corrector import corrector

print("=== SQL Corrector Test Suite ===\n")

# Test 1: Valid SQL (should execute without correction)
print("Test 1: Valid SQL")
sql1 = "SELECT CustomerName, PhoneNumber FROM customers LIMIT 5"
result1 = corrector.execute_with_retry(sql1)
print(f"  SQL: {sql1}")
print(f"  Success: {result1['success']}")
print(f"  Correction Applied: {result1['correction_applied']}")
print(f"  Message: {result1['message']}")
print(f"  Rows returned: {len(result1['data']) if result1['data'] is not None else 0}\n")

# Test 2: SQL with incorrect alias (should auto-correct)
print("Test 2: SQL with incorrect alias")
sql2 = "SELECT c.CustomerID, c.CustomerName FROM customers c WHERE c.City = 'Mumbai'"
result2 = corrector.execute_with_retry(sql2)
print(f"  Original SQL: {result2['original_sql']}")
print(f"  Success: {result2['success']}")
print(f"  Correction Applied: {result2['correction_applied']}")
if result2['correction_applied']:
    print(f"  Corrected SQL: {result2['sql_used']}")
print(f"  Message: {result2['message']}")
print(f"  Rows returned: {len(result2['data']) if result2['data'] is not None else 0}\n")

# Test 3: Schema information
print("Test 3: Schema Cache")
print(f"  Tables loaded: {len(corrector.schema_cache)}")
print(f"  Tables: {list(corrector.schema_cache.keys())}")
print(f"\n  Customers table columns: {corrector.schema_cache.get('customers', [])}\n")

# Test 4: Column lookup
print("Test 4: Column Lookup")
test_columns = ['CustomerName', 'PhoneNumber', 'City', 'ManagerID']
for col in test_columns:
    matches = corrector.find_column_in_schema(col)
    print(f"  '{col}' found in: {matches}")

print("\n✅ SQL Corrector tests completed!")
