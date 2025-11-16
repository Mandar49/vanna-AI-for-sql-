"""
Schema Awareness Demo
Demonstrates dynamic schema awareness and relationship inference
"""
from sql_corrector import corrector

def demo_schema_loading():
    """Demonstrate schema loading"""
    print("\n" + "="*70)
    print("DEMO 1: Schema Loading")
    print("="*70)
    
    print(f"\n[INFO] Loaded {len(corrector.schema_cache)} tables:")
    
    for table in sorted(corrector.schema_cache.keys()):
        columns = corrector.schema_cache[table]
        print(f"\n   {table} ({len(columns)} columns):")
        print(f"      {', '.join(columns[:5])}")
        if len(columns) > 5:
            print(f"      ... and {len(columns) - 5} more")

def demo_relationship_inference():
    """Demonstrate relationship inference"""
    print("\n" + "="*70)
    print("DEMO 2: Relationship Inference")
    print("="*70)
    
    tables = ['salesorders', 'customers', 'orderitems']
    
    for table in tables:
        relationships = corrector.infer_relationships(table)
        
        print(f"\n[{table}] can join to:")
        
        if relationships:
            for rel in relationships:
                print(f"   -> {rel['target_table']}")
                print(f"      ON {table}.{rel['source_column']} = {rel['target_table']}.{rel['target_column']}")
                print(f"      Type: {rel['join_type']} JOIN")
        else:
            print("   (no relationships defined)")

def demo_column_validation():
    """Demonstrate column validation"""
    print("\n" + "="*70)
    print("DEMO 3: Column Validation")
    print("="*70)
    
    tests = [
        ('salesorders', 'OrderID', True),
        ('salesorders', 'TotalAmount', True),
        ('salesorders', 'InvalidColumn', False),
        ('customers', 'CustomerName', True),
    ]
    
    for table, column, expected in tests:
        try:
            exists = corrector.validate_column_exists(table, column)
            status = "[OK]" if exists == expected else "[FAIL]"
            result = "exists" if exists else "does not exist"
            print(f"{status} {table}.{column} {result}")
        except ValueError as e:
            print(f"[ERROR] {e}")

def demo_join_builder():
    """Demonstrate dynamic JOIN builder"""
    print("\n" + "="*70)
    print("DEMO 4: Dynamic JOIN Builder")
    print("="*70)
    
    joins = [
        ('salesorders', 'customers'),
        ('salesorders', 'employees'),
        ('orderitems', 'products'),
        ('customers', 'products'),  # No direct relationship
    ]
    
    for from_table, to_table in joins:
        join_clause = corrector.build_join_clause(from_table, to_table)
        
        print(f"\n[JOIN] {from_table} -> {to_table}:")
        
        if join_clause:
            print(f"   {join_clause}")
        else:
            print("   (no direct relationship)")

def demo_query_introspection():
    """Demonstrate query introspection"""
    print("\n" + "="*70)
    print("DEMO 5: Query Introspection")
    print("="*70)
    
    queries = [
        ("Valid query", "SELECT so.OrderID, c.CustomerName FROM salesorders so JOIN customers c"),
        ("Invalid column", "SELECT so.InvalidColumn FROM salesorders so"),
    ]
    
    for name, sql in queries:
        print(f"\n[TEST] {name}:")
        print(f"   SQL: {sql[:60]}...")
        
        result = corrector.introspect_query_columns(sql)
        
        print(f"   Valid: {result['valid']}")
        print(f"   Tables: {result['tables_used']}")
        
        if result['invalid_columns']:
            print(f"   Invalid columns: {result['invalid_columns']}")

def demo_complete_example():
    """Demonstrate complete example"""
    print("\n" + "="*70)
    print("DEMO 6: Complete Example - Building a Query Dynamically")
    print("="*70)
    
    # Start with base table
    base_table = 'salesorders'
    print(f"\n[STEP 1] Starting with table: {base_table}")
    
    # Get available columns
    columns = corrector.get_table_columns(base_table)
    print(f"[STEP 2] Available columns: {', '.join(columns[:3])}...")
    
    # Find relationships
    relationships = corrector.infer_relationships(base_table)
    print(f"[STEP 3] Found {len(relationships)} relationships")
    
    # Build JOIN to customers
    join_clause = corrector.build_join_clause(base_table, 'customers')
    print(f"[STEP 4] Generated JOIN clause:")
    print(f"   {join_clause}")
    
    # Build complete query
    sql = f"""
    SELECT 
        so.OrderID,
        so.TotalAmount,
        c.CustomerName
    FROM {base_table} so
    {join_clause}
    LIMIT 5
    """
    
    print(f"\n[STEP 5] Complete query:")
    print(sql)
    
    # Validate query
    introspection = corrector.introspect_query_columns(sql)
    print(f"\n[STEP 6] Validation:")
    print(f"   Valid: {introspection['valid']}")
    print(f"   Tables used: {introspection['tables_used']}")
    
    # Execute query
    print(f"\n[STEP 7] Executing query...")
    result = corrector.execute_with_retry(sql, max_retries=0)
    
    if result['success']:
        print(f"   [OK] Query executed successfully")
        print(f"   [OK] Schema validated: {result['schema_validated']}")
        print(f"   [OK] Rows returned: {result['row_count']}")
    else:
        print(f"   [FAIL] Query failed: {result['message']}")

def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("SCHEMA AWARENESS DEMONSTRATION")
    print("="*70)
    print("\nDemonstrating:")
    print("1. Schema loading and caching")
    print("2. Automatic relationship inference")
    print("3. Column validation")
    print("4. Dynamic JOIN clause generation")
    print("5. Query introspection")
    print("6. Complete example")
    
    try:
        demo_schema_loading()
        demo_relationship_inference()
        demo_column_validation()
        demo_join_builder()
        demo_query_introspection()
        demo_complete_example()
        
        print("\n" + "="*70)
        print("KEY FEATURES")
        print("="*70)
        print("""
[OK] Dynamic schema awareness
[OK] Automatic relationship inference
[OK] Column validation before execution
[OK] Dynamic JOIN clause generation
[OK] Query introspection and validation
[OK] Safe fallback for missing columns/tables
[OK] Backward compatibility maintained
        """)
        
        print("\n" + "="*70)
        print("BENEFITS")
        print("="*70)
        print("""
- No hard-coded JOINs required
- Queries validated before execution
- Clear error messages for invalid columns
- Adapts to schema changes automatically
- Maintains backward compatibility
        """)
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
