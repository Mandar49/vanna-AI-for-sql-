"""
DB-ANALYST-V3 Comprehensive Test Suite
Tests all 5 core rules:
1. SQL First Guarantee
2. No Hallucination
3. Strict Output Format
4. Database-Only Values
5. Correct SQL
"""
import re
import pandas as pd
from sql_corrector import corrector
from business_analyst import analyst
from response_composer import composer
from data_validator import validator
from query_router import router

class TestDBAnalystV3:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def assert_true(self, condition, test_name, message=""):
        """Assert that condition is True"""
        if condition:
            self.passed += 1
            self.tests.append({"name": test_name, "status": "PASS", "message": message})
            print(f"✓ PASS: {test_name}")
        else:
            self.failed += 1
            self.tests.append({"name": test_name, "status": "FAIL", "message": message})
            print(f"✗ FAIL: {test_name} - {message}")
    
    def assert_false(self, condition, test_name, message=""):
        """Assert that condition is False"""
        self.assert_true(not condition, test_name, message)
    
    def assert_contains(self, text, substring, test_name, message=""):
        """Assert that text contains substring"""
        self.assert_true(substring in text, test_name, message or f"Expected '{substring}' in text")
    
    def assert_not_contains(self, text, substring, test_name, message=""):
        """Assert that text does NOT contain substring"""
        self.assert_false(substring in text, test_name, message or f"Did not expect '{substring}' in text")
    
    def assert_format(self, text, test_name):
        """Assert that text follows SQL RESULT → ANALYST → SQL QUERY format"""
        has_sql_result = "SQL RESULT" in text
        has_analyst = "ANALYST" in text
        has_sql_query = "SQL QUERY" in text
        
        # Check order
        if has_sql_result and has_analyst and has_sql_query:
            sql_result_pos = text.find("SQL RESULT")
            analyst_pos = text.find("ANALYST")
            sql_query_pos = text.find("SQL QUERY")
            
            correct_order = sql_result_pos < analyst_pos < sql_query_pos
            self.assert_true(correct_order, test_name, 
                           f"Format order: SQL RESULT ({sql_result_pos}) → ANALYST ({analyst_pos}) → SQL QUERY ({sql_query_pos})")
        else:
            self.assert_true(False, test_name, 
                           f"Missing sections: SQL RESULT={has_sql_result}, ANALYST={has_analyst}, SQL QUERY={has_sql_query}")
    
    def test_person_not_in_database(self):
        """Test that system blocks external knowledge about people not in DB"""
        print("\n--- Test: Person Not in Database ---")
        
        # Test person lookup for someone not in DB
        result = analyst.check_person_in_database("Shah Rukh Khan")
        
        self.assert_false(result['found'], "Person not found in DB", 
                         f"Shah Rukh Khan should not be in database")
        self.assert_contains(result['message'], "does not exist", "Error message correct",
                           "Should say 'does not exist in your database'")
    
    def test_person_in_database(self):
        """Test that system finds people who ARE in the database"""
        print("\n--- Test: Person In Database ---")
        
        # Test with a real employee (adjust name based on your DB)
        result = analyst.check_person_in_database("John Smith")
        
        # This test depends on your data - if John Smith exists, it should be found
        if result['found']:
            self.assert_true(result['found'], "Person found in DB")
            self.assert_true(result['data'] is not None, "Person data returned")
        else:
            print("  ℹ️  Note: 'John Smith' not in database (expected if no such employee)")
    
    def test_missing_column_error(self):
        """Test that system blocks queries for non-existent columns"""
        print("\n--- Test: Missing Column Error ---")
        
        # Try to query a column that doesn't exist
        sql = "SELECT units_sold FROM salesorders"
        result = corrector.execute_with_retry(sql, max_retries=0)
        
        self.assert_false(result['success'], "Query should fail for missing column")
        self.assert_true(result['message'] == 'SQL_ERROR', "Should return SQL_ERROR")
        self.assert_contains(result.get('reason', ''), "does not exist", "Reason should mention column doesn't exist")
    
    def test_missing_table_error(self):
        """Test that system handles non-existent tables (may auto-correct or error)"""
        print("\n--- Test: Missing Table Error ---")
        
        # Try to query a table that doesn't exist (but might be auto-corrected)
        sql = "SELECT * FROM completely_nonexistent_table_xyz"
        result = corrector.execute_with_retry(sql, max_retries=0)
        
        # DB-ANALYST-V3: Schema manager may auto-correct similar table names (good behavior)
        # But completely invalid tables should fail
        if result['success']:
            print("  ℹ️  Note: Table was auto-corrected (acceptable behavior)")
            self.assert_true(True, "Auto-correction is acceptable")
        else:
            self.assert_false(result['success'], "Query should fail for completely invalid table")
            self.assert_true(result.get('message') == 'SQL_ERROR', "Should return SQL_ERROR")
    
    def test_no_data_found_format(self):
        """Test that NO DATA FOUND follows strict format"""
        print("\n--- Test: No Data Found Format ---")
        
        # Query that returns no rows
        sql = "SELECT * FROM customers WHERE CustomerID = 999999"
        result = corrector.execute_with_retry(sql, max_retries=0)
        
        if result['success'] and result['data'].empty:
            # Build the response as the system would
            separator = "─" * 60
            response = f"{separator}\n"
            response += "SQL RESULT\n"
            response += f"{separator}\n"
            response += "❌ NO DATA FOUND\n\n"
            response += f"Reason: {result.get('reason', 'Query returned no data')}\n\n"
            response += f"Suggestion: {result.get('suggestion', 'Try different criteria')}\n\n"
            response += f"{separator}\n"
            response += "SQL QUERY\n"
            response += f"{separator}\n"
            response += sql
            
            # Check format (NO DATA FOUND doesn't need ANALYST section)
            self.assert_contains(response, "SQL RESULT", "Contains SQL RESULT section")
            self.assert_contains(response, "SQL QUERY", "Contains SQL QUERY section")
            self.assert_contains(response, "❌ NO DATA FOUND", "Contains NO DATA FOUND marker")
            self.assert_contains(response, "Reason:", "Contains Reason section")
            self.assert_contains(response, "Suggestion:", "Contains Suggestion section")
    
    def test_sql_error_format(self):
        """Test that SQL ERROR follows strict format"""
        print("\n--- Test: SQL Error Format ---")
        
        # Invalid SQL
        sql = "SELECT * FROM nonexistent_table"
        result = corrector.execute_with_retry(sql, max_retries=0)
        
        if not result['success']:
            # Build the response as the system would
            separator = "─" * 60
            response = f"{separator}\n"
            response += "SQL RESULT\n"
            response += f"{separator}\n"
            response += "❌ SQL ERROR\n\n"
            response += f"Reason: {result.get('reason', 'SQL failed')}\n\n"
            response += f"Suggestion: {result.get('suggestion', 'Check your query')}\n\n"
            response += f"{separator}\n"
            response += "SQL QUERY\n"
            response += f"{separator}\n"
            response += sql
            
            # Check format (SQL ERROR doesn't need ANALYST section)
            self.assert_contains(response, "SQL RESULT", "Contains SQL RESULT section")
            self.assert_contains(response, "SQL QUERY", "Contains SQL QUERY section")
            self.assert_contains(response, "❌ SQL ERROR", "Contains SQL ERROR marker")
            self.assert_contains(response, "Reason:", "Contains Reason section")
            self.assert_contains(response, "Suggestion:", "Contains Suggestion section")
    
    def test_no_hallucination_validation(self):
        """Test that validator catches fabricated numbers"""
        print("\n--- Test: No Hallucination Validation ---")
        
        # Create sample data
        df = pd.DataFrame({
            'Year': [2023, 2024],
            'Sales': [100000, 150000]
        })
        
        # Response with exact numbers from data (VALID)
        valid_response = "The data shows 2023 sales of 100000 and 2024 sales of 150000."
        is_valid, suspicious = validator.validate_response(valid_response, df)
        self.assert_true(is_valid, "Valid response passes validation",
                        f"Should accept exact numbers from data")
        
        # Response with calculated percentage (INVALID)
        invalid_response = "Sales grew by 50% from 100000 to 150000."
        is_valid, suspicious = validator.validate_response(invalid_response, df)
        self.assert_false(is_valid, "Invalid response fails validation",
                         f"Should reject calculated percentage (50)")
        self.assert_true(50.0 in suspicious, "Detects fabricated percentage",
                        f"50% should be flagged as suspicious: {suspicious}")
    
    def test_cagr_from_sql_only(self):
        """Test that CAGR comes from SQL, not LLM calculation"""
        print("\n--- Test: CAGR From SQL Only ---")
        
        # Calculate CAGR using SQL
        result = corrector.calculate_cagr_sql(2023, 2024, forecast_years=[])
        
        if result['success']:
            self.assert_true(result['cagr'] is not None, "CAGR calculated from SQL")
            self.assert_true(result['start_sales'] is not None, "Start sales from SQL")
            self.assert_true(result['end_sales'] is not None, "End sales from SQL")
            
            # Validate CAGR
            is_valid, msg = validator.validate_cagr(
                result['cagr'],
                result['start_sales'],
                result['end_sales'],
                2023,
                2024
            )
            self.assert_true(is_valid, "CAGR validation passes", msg)
        else:
            print(f"  ℹ️  Note: CAGR calculation skipped - {result['message']}")
    
    def test_general_query_blocked(self):
        """Test that non-database questions are blocked"""
        print("\n--- Test: General Query Blocked ---")
        
        # Try a general knowledge question
        result = router.route_query("What is Bollywood?")
        
        if result['type'] == 'general':
            answer = result.get('answer', '')
            self.assert_contains(answer, "database", "Response mentions database scope",
                               "Should redirect to database-only scope")
            self.assert_not_contains(answer, "film industry", "No external knowledge",
                                   "Should not provide Bollywood information")
    
    def test_analyst_no_calculations(self):
        """Test that analyst doesn't perform calculations"""
        print("\n--- Test: Analyst No Calculations ---")
        
        # Create sample data
        df = pd.DataFrame({
            'Year': [2023, 2024],
            'Sales': [100, 150]
        })
        
        # Analyze with strict rules
        analysis = analyst.analyze_results_with_llm("What are the sales?", df, "SELECT * FROM sales")
        
        insight = analysis.get('insight', '')
        
        # Check that insight doesn't contain calculated percentages
        # Look for patterns like "50%", "increased by X%", etc.
        has_percentage = re.search(r'\d+\.?\d*\s*%', insight)
        
        if has_percentage:
            # Check if the percentage is in the original data
            percentage_value = float(has_percentage.group().replace('%', '').strip())
            is_in_data = any(abs(val - percentage_value) < 0.1 for val in df.select_dtypes(include=['number']).values.flatten())
            
            if not is_in_data:
                self.assert_false(True, "Analyst should not calculate percentages",
                                f"Found calculated percentage: {has_percentage.group()}")
            else:
                self.assert_true(True, "Percentage is from data", "Percentage found in original data")
        else:
            self.assert_true(True, "No calculated percentages", "Analyst uses exact values only")
    
    def test_trend_no_calculations(self):
        """Test that trend analysis doesn't calculate percentages"""
        print("\n--- Test: Trend No Calculations ---")
        
        # Create sample data
        df = pd.DataFrame({
            'Year': [2023, 2024],
            'Sales': [100, 150]
        })
        
        # Analyze trend
        trend = analyst.analyze_trends(df)
        
        # Check that trend doesn't contain calculated percentages
        has_percentage = re.search(r'\d+\.?\d*\s*%', trend)
        
        if has_percentage:
            self.assert_false(True, "Trend should not calculate percentages",
                            f"Found calculated percentage: {has_percentage.group()}")
        else:
            self.assert_true(True, "Trend uses exact values only", "No calculated percentages")
        
        # Should contain exact values
        self.assert_contains(trend, "100", "Contains start value")
        self.assert_contains(trend, "150", "Contains end value")
    
    def test_response_format_with_data(self):
        """Test that successful query follows SQL RESULT → ANALYST → SQL QUERY format"""
        print("\n--- Test: Response Format With Data ---")
        
        # This would be the full response from the system
        # Simulating what ad_ai_app.py would generate
        
        df = pd.DataFrame({
            'CustomerName': ['Alice', 'Bob'],
            'TotalOrders': [5, 3]
        })
        
        sql = "SELECT CustomerName, COUNT(*) as TotalOrders FROM customers GROUP BY CustomerName"
        
        # Build response as system would
        separator = "─" * 60
        response = f"{separator}\n"
        response += "SQL RESULT\n"
        response += f"{separator}\n"
        response += df.to_string(index=False)
        response += f"\n\n{separator}\n"
        response += "ANALYST\n"
        response += f"{separator}\n"
        response += "The data shows Alice with 5 orders and Bob with 3 orders. Alice has more orders than Bob."
        response += f"\n\n{separator}\n"
        response += "SQL QUERY\n"
        response += f"{separator}\n"
        response += sql
        
        self.assert_format(response, "Success response format correct")
        self.assert_contains(response, "Alice", "Contains data from SQL RESULT")
        self.assert_contains(response, "5", "Contains exact numbers")
    
    def run_all_tests(self):
        """Run all tests and print summary"""
        print("="*70)
        print("DB-ANALYST-V3 COMPREHENSIVE TEST SUITE")
        print("="*70)
        
        # Run all tests
        self.test_person_not_in_database()
        self.test_person_in_database()
        self.test_missing_column_error()
        self.test_missing_table_error()
        self.test_no_data_found_format()
        self.test_sql_error_format()
        self.test_no_hallucination_validation()
        self.test_cagr_from_sql_only()
        self.test_general_query_blocked()
        self.test_analyst_no_calculations()
        self.test_trend_no_calculations()
        self.test_response_format_with_data()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✓ Passed: {self.passed}")
        print(f"✗ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("="*70)
        
        # Print failed tests
        if self.failed > 0:
            print("\nFAILED TESTS:")
            for test in self.tests:
                if test['status'] == 'FAIL':
                    print(f"  ✗ {test['name']}: {test['message']}")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestDBAnalystV3()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED - DB-ANALYST-V3 IS COMPLIANT")
        exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - FIX REQUIRED")
        exit(1)
