"""
Test Schema Awareness and Dynamic Relationship Inference
Verifies backward compatibility with existing tests
"""
from sql_corrector import corrector

def test_schema_loading():
    """Test 1: Schema loading"""
    print("\n" + "="*70)
    print("TEST 1: Schema Loading")
    print("="*70)
    
    if corrector.schema_cache:
        print(f"\n[OK] Schema loaded: {len(corrector.schema_cache)} tables")
        
        # Show tables
        for table in sorted(corrector.schema_cache.keys()):
            col_count = len(corrector.schema_cache[table])
            print(f"   - {table}: {col_count} columns")
        
        print("\n[PASS] Schema loading successful")
        return True
    else:
        print("\n[FAIL] Schema not loaded")
        return False

def test_relationship_inference():
    """Test 2: Relationship inference"""
    print("\n" + "="*70)
    print("TEST 2: Relationship Inference")
    print("="*70)
    
    test_tables = ['salesorders', 'customers', 'orderitems', 'products']
    
    all_passed = True
    
    for table in test_tables:
        relationships = corrector.infer_relationships(table)
        
        print(f"\n[TEST] Relationships for '{table}':")
        
        if relationships:
            for rel in relationships:
                print(f"   → {rel['target_table']} via {rel['source_column']} = {rel['target_column']} ({rel['join_type']})")
            print(f"   [OK] Found {len(relationships)} relationship(s)")
        else:
            print(f"   [INFO] No relationships defined")
    
    # Test specific relationship
    salesorders_rels = corrector.infer_relationships('salesorders')
    has_customer_rel = any(r['target_table'] == 'customers' for r in salesorders_rels)
    
    if has_customer_rel:
        print("\n[PASS] Relationship inference working correctly")
        return True
    else:
        print("\n[FAIL] Expected relationship not found")
        return False

def test_column_validation():
    """Test 3: Column validation"""
    print("\n" + "="*70)
    print("TEST 3: Column Validation")
    print("="*70)
    
    # Test valid column
    print("\n[TEST] Validating valid column:")
    try:
        is_valid = corrector.validate_column_exists('salesorders', 'OrderID')
        if is_valid:
            print("   [OK] salesorders.OrderID exists")
        else:
            print("   [FAIL] salesorders.OrderID not found")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test invalid column
    print("\n[TEST] Validating invalid column:")
    try:
        is_valid = corrector.validate_column_exists('salesorders', 'InvalidColumn')
        if not is_valid:
            print("   [OK] InvalidColumn correctly identified as missing")
        else:
            print("   [FAIL] InvalidColumn incorrectly validated")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test invalid table
    print("\n[TEST] Validating invalid table:")
    try:
        is_valid = corrector.validate_column_exists('InvalidTable', 'OrderID')
        print("   [FAIL] Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"   [OK] Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"   [ERROR] Unexpected error: {e}")
        return False
    
    print("\n[PASS] Column validation working correctly")
    return True

def test_query_introspection():
    """Test 4: Query introspection"""
    print("\n" + "="*70)
    print("TEST 4: Query Introspection")
    print("="*70)
    
    # Test valid query
    valid_sql = """
    SELECT so.OrderID, c.CustomerName, so.TotalAmount
    FROM salesorders so
    JOIN customers c ON so.CustomerID = c.CustomerID
    """
    
    print("\n[TEST] Introspecting valid query:")
    introspection = corrector.introspect_query_columns(valid_sql)
    
    print(f"   Valid: {introspection['valid']}")
    print(f"   Tables used: {introspection['tables_used']}")
    print(f"   Invalid columns: {introspection['invalid_columns']}")
    
    if introspection['valid']:
        print("   [OK] Valid query passed introspection")
    else:
        print("   [FAIL] Valid query failed introspection")
        return False
    
    # Test invalid query
    invalid_sql = """
    SELECT so.InvalidColumn, c.FakeColumn
    FROM salesorders so
    JOIN customers c ON so.CustomerID = c.CustomerID
    """
    
    print("\n[TEST] Introspecting invalid query:")
    introspection = corrector.introspect_query_columns(invalid_sql)
    
    print(f"   Valid: {introspection['valid']}")
    print(f"   Invalid columns: {introspection['invalid_columns']}")
    
    if not introspection['valid'] and len(introspection['invalid_columns']) > 0:
        print("   [OK] Invalid columns detected")
    else:
        print("   [FAIL] Invalid columns not detected")
        return False
    
    print("\n[PASS] Query introspection working correctly")
    return True

def test_join_clause_builder():
    """Test 5: Dynamic JOIN clause builder"""
    print("\n" + "="*70)
    print("TEST 5: Dynamic JOIN Clause Builder")
    print("="*70)
    
    # Test salesorders → customers join
    print("\n[TEST] Building JOIN: salesorders → customers")
    join_clause = corrector.build_join_clause('salesorders', 'customers')
    
    if join_clause:
        print(f"   Generated: {join_clause}")
        
        if 'CustomerID' in join_clause:
            print("   [OK] JOIN clause generated correctly")
        else:
            print("   [FAIL] JOIN clause missing CustomerID")
            return False
    else:
        print("   [FAIL] No JOIN clause generated")
        return False
    
    # Test orderitems → products join
    print("\n[TEST] Building JOIN: orderitems → products")
    join_clause = corrector.build_join_clause('orderitems', 'products')
    
    if join_clause:
        print(f"   Generated: {join_clause}")
        print("   [OK] JOIN clause generated")
    else:
        print("   [FAIL] No JOIN clause generated")
        return False
    
    # Test non-existent relationship
    print("\n[TEST] Building JOIN: customers → products (no direct relationship)")
    join_clause = corrector.build_join_clause('customers', 'products')
    
    if not join_clause:
        print("   [OK] Correctly returned empty string for non-existent relationship")
    else:
        print("   [FAIL] Should not generate JOIN for non-existent relationship")
        return False
    
    print("\n[PASS] JOIN clause builder working correctly")
    return True

def test_backward_compatibility():
    """Test 6: Backward compatibility with existing tests"""
    print("\n" + "="*70)
    print("TEST 6: Backward Compatibility")
    print("="*70)
    
    # Test existing CAGR calculation
    print("\n[TEST] CAGR calculation (existing functionality):")
    result = corrector.calculate_cagr_sql(2023, 2024)
    
    if result['success']:
        print(f"   [OK] CAGR: {result['cagr']}%")
        print(f"   [OK] Schema validated: {result.get('schema_validated', 'N/A')}")
    else:
        print(f"   [FAIL] CAGR calculation failed: {result['message']}")
        return False
    
    # Test existing SQL execution
    print("\n[TEST] SQL execution (existing functionality):")
    sql = "SELECT COUNT(*) AS TotalOrders FROM salesorders"
    result = corrector.execute_with_retry(sql, max_retries=0)
    
    if result['success']:
        print(f"   [OK] Query executed successfully")
        print(f"   [OK] Schema validated: {result.get('schema_validated', False)}")
        print(f"   [OK] Row count: {result['row_count']}")
    else:
        print(f"   [FAIL] Query execution failed: {result['message']}")
        return False
    
    print("\n[PASS] Backward compatibility maintained")
    return True

def test_schema_validation_in_execution():
    """Test 7: Schema validation during execution"""
    print("\n" + "="*70)
    print("TEST 7: Schema Validation in Execution")
    print("="*70)
    
    # Test query with invalid column
    print("\n[TEST] Executing query with invalid column:")
    invalid_sql = "SELECT InvalidColumn FROM salesorders"
    result = corrector.execute_with_retry(invalid_sql, max_retries=0)
    
    if not result['success']:
        print(f"   [OK] Query rejected: {result['message']}")
        
        if 'Invalid columns' in result['message']:
            print("   [OK] Schema validation working in execution")
        else:
            print("   [WARN] Error message doesn't mention schema validation")
    else:
        print("   [FAIL] Invalid query was accepted")
        return False
    
    # Test query with valid columns
    print("\n[TEST] Executing query with valid columns:")
    valid_sql = "SELECT OrderID, TotalAmount FROM salesorders LIMIT 5"
    result = corrector.execute_with_retry(valid_sql, max_retries=0)
    
    if result['success']:
        print(f"   [OK] Query executed successfully")
        print(f"   [OK] Schema validated: {result.get('schema_validated', False)}")
    else:
        print(f"   [FAIL] Valid query failed: {result['message']}")
        return False
    
    print("\n[PASS] Schema validation in execution working correctly")
    return True

def run_all_tests():
    """Run all schema awareness tests"""
    print("\n" + "="*70)
    print("SCHEMA AWARENESS TEST SUITE")
    print("="*70)
    print("[INFO] Testing dynamic schema awareness and relationship inference")
    print("[INFO] Verifying backward compatibility with existing tests")
    
    results = []
    
    try:
        results.append(("Schema Loading", test_schema_loading()))
        results.append(("Relationship Inference", test_relationship_inference()))
        results.append(("Column Validation", test_column_validation()))
        results.append(("Query Introspection", test_query_introspection()))
        results.append(("JOIN Clause Builder", test_join_clause_builder()))
        results.append(("Backward Compatibility", test_backward_compatibility()))
        results.append(("Schema Validation in Execution", test_schema_validation_in_execution()))
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status} {name}")
        
        print(f"\n[INFO] Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n[SUCCESS] All schema awareness tests passed!")
            print("[INFO] Dynamic schema awareness implemented")
            print("[INFO] Backward compatibility maintained")
            return 0
        else:
            print(f"\n[WARNING] {total - passed} test(s) failed")
            return 1
            
    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    exit_code = run_all_tests()
    sys.exit(exit_code)
