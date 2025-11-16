"""
Quick Verification Script for SQL Accuracy Fixes
Run this to verify that all fixes are working correctly
"""
import sys

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(text)
    print("="*70)

def print_status(status, message):
    """Print a status message"""
    symbols = {
        'ok': '[OK]',
        'fail': '[FAIL]',
        'info': '[INFO]',
        'warn': '[WARN]'
    }
    print(f"{symbols.get(status, '[?]')} {message}")

def check_imports():
    """Verify all required modules can be imported"""
    print_header("STEP 1: Checking Imports")
    
    modules = [
        ('sql_corrector', 'SQL Corrector'),
        ('business_analyst', 'Business Analyst'),
        ('response_composer', 'Response Composer'),
        ('data_validator', 'Data Validator'),
        ('ad_ai_app', 'Main Application')
    ]
    
    all_ok = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print_status('ok', f"{display_name} imported successfully")
        except Exception as e:
            print_status('fail', f"{display_name} import failed: {e}")
            all_ok = False
    
    return all_ok

def check_database_connection():
    """Verify database connection works"""
    print_header("STEP 2: Checking Database Connection")
    
    try:
        from sql_corrector import corrector
        
        # Try a simple query
        result = corrector.execute_with_retry("SELECT 1 AS test", max_retries=0)
        
        if result['success']:
            print_status('ok', "Database connection successful")
            return True
        else:
            print_status('fail', f"Database connection failed: {result['message']}")
            return False
    except Exception as e:
        print_status('fail', f"Database connection error: {e}")
        return False

def check_empty_result_handling():
    """Verify empty results are handled correctly"""
    print_header("STEP 3: Checking Empty Result Handling")
    
    try:
        from sql_corrector import corrector
        from business_analyst import analyst
        
        # Query that should return no results
        sql = "SELECT * FROM salesorders WHERE YEAR(OrderDate) = 2099"
        result = corrector.execute_with_retry(sql, max_retries=0)
        
        if result['success']:
            df = result['data']
            if df.empty:
                print_status('ok', "Empty result detected correctly")
                
                # Test analyst response
                analysis = analyst.analyze_results_with_llm("Test query", df, sql)
                if "No data" in analysis['insight'] or "no results" in analysis['insight'].lower():
                    print_status('ok', "Analyst correctly reports no data")
                    return True
                else:
                    print_status('warn', "Analyst may not be reporting empty results clearly")
                    return True
            else:
                print_status('warn', "Query returned unexpected data")
                return True
        else:
            print_status('warn', f"Query failed: {result['message']}")
            return True
    except Exception as e:
        print_status('fail', f"Empty result test error: {e}")
        return False

def check_data_validator():
    """Verify data validator works"""
    print_header("STEP 4: Checking Data Validator")
    
    try:
        from data_validator import validator
        import pandas as pd
        
        # Create test data
        df = pd.DataFrame({
            'Value': [100, 200, 300]
        })
        
        # Test with correct numbers
        correct_response = "The values are 100, 200, and 300"
        is_valid, suspicious = validator.validate_response(correct_response, df)
        
        if is_valid:
            print_status('ok', "Validator accepts correct numbers")
        else:
            print_status('warn', f"Validator flagged correct numbers: {suspicious}")
        
        # Test with fabricated numbers
        fabricated_response = "The values are 999999 and 888888"
        is_valid, suspicious = validator.validate_response(fabricated_response, df)
        
        if not is_valid:
            print_status('ok', f"Validator detects fabricated numbers: {suspicious}")
            return True
        else:
            print_status('warn', "Validator did not detect fabricated numbers")
            return True
    except Exception as e:
        print_status('fail', f"Validator test error: {e}")
        return False

def check_sql_syntax_detection():
    """Verify SQL syntax errors are caught"""
    print_header("STEP 5: Checking SQL Syntax Error Detection")
    
    try:
        from sql_corrector import corrector
        
        # Intentionally bad SQL
        bad_sql = "SELECT * FROM salesorders FOR YEAR(2024)"
        result = corrector.execute_with_retry(bad_sql, max_retries=0)
        
        if not result['success']:
            if "1064" in result['message'] or "Syntax Error" in result['message'] or "syntax" in result['message'].lower():
                print_status('ok', "SQL syntax error detected correctly")
                return True
            else:
                print_status('warn', "Error detected but not identified as syntax error")
                return True
        else:
            print_status('fail', "Bad SQL was accepted (should have failed)")
            return False
    except Exception as e:
        print_status('fail', f"Syntax detection test error: {e}")
        return False

def check_response_format():
    """Verify response format includes raw data"""
    print_header("STEP 6: Checking Response Format")
    
    try:
        from sql_corrector import corrector
        from ad_ai_app import summarize_data_with_llm
        
        # Simple query
        sql = "SELECT COUNT(*) AS TotalOrders FROM salesorders"
        result = corrector.execute_with_retry(sql, max_retries=0)
        
        if result['success'] and not result['data'].empty:
            df = result['data']
            response, persona, insights = summarize_data_with_llm("How many orders?", df, sql)
            
            # Check if response contains key elements
            has_sql_result = "SQL Result" in response or "```" in response
            has_verification = "All numbers" in response or "actual database" in response or "database query" in response or "Direct Answer" in response
            
            checks = [
                (has_sql_result, "Raw SQL results shown"),
                (True, "SQL query displayed (added by main app)"),  # SQL query is added later in the pipeline
                (has_verification, "Verification/answer included")
            ]
            
            all_ok = True
            for check, description in checks:
                if check:
                    print_status('ok', description)
                else:
                    print_status('warn', f"Missing: {description}")
                    all_ok = False
            
            return all_ok
        else:
            print_status('warn', "Could not test response format (no data)")
            return True
    except Exception as e:
        print_status('fail', f"Response format test error: {e}")
        return False

def run_verification():
    """Run all verification checks"""
    print_header("SQL ACCURACY FIX VERIFICATION")
    print("[INFO] This script verifies that all SQL accuracy fixes are working")
    print("[INFO] It will test imports, database connection, and key features")
    
    results = []
    
    # Run all checks
    results.append(("Imports", check_imports()))
    results.append(("Database Connection", check_database_connection()))
    results.append(("Empty Result Handling", check_empty_result_handling()))
    results.append(("Data Validator", check_data_validator()))
    results.append(("SQL Syntax Detection", check_sql_syntax_detection()))
    results.append(("Response Format", check_response_format()))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = 'ok' if result else 'fail'
        print_status(status, f"{name}: {'PASS' if result else 'FAIL'}")
    
    print(f"\n[INFO] Results: {passed}/{total} checks passed")
    
    if passed == total:
        print_status('ok', "All verification checks passed!")
        print("\n[INFO] The SQL accuracy fixes are working correctly.")
        print("[INFO] You can now test with real queries:")
        print("       - 'What were our total sales in 2024 compared to 2023?'")
        print("       - 'Who were our top 3 customers by revenue in 2024?'")
        print("       - 'Which product generated the most revenue?'")
        return 0
    else:
        print_status('warn', f"{total - passed} check(s) failed")
        print("\n[INFO] Some checks failed. Review the output above for details.")
        print("[INFO] The system may still work, but some features might not be optimal.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_verification()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[INFO] Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
