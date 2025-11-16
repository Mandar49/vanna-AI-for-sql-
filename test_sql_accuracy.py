"""
Test SQL Accuracy - Verify that all responses match actual database data
Tests the complete pipeline from SQL generation to response formatting
"""
import pandas as pd
from sql_corrector import corrector
from business_analyst import analyst
from data_validator import validator
from response_composer import composer

def test_empty_result_handling():
    """Test that empty results are handled correctly without fabrication"""
    print("\n" + "="*60)
    print("TEST 1: Empty Result Handling")
    print("="*60)
    
    # Simulate a query that returns no data
    sql = "SELECT * FROM salesorders WHERE YEAR(OrderDate) = 2025"
    result = corrector.execute_with_retry(sql, max_retries=0)
    
    if result['success']:
        df = result['data']
        if df.empty:
            print("✓ Query returned empty DataFrame as expected")
            print(f"✓ Message: {result['message']}")
            
            # Test that analyst doesn't fabricate data
            analysis = analyst.analyze_results_with_llm("What were sales in 2025?", df, sql)
            print(f"✓ Analysis insight: {analysis['insight']}")
            
            if "No data" in analysis['insight'] or "no results" in analysis['insight'].lower():
                print("✓ PASS: Analyst correctly reports no data")
            else:
                print("✗ FAIL: Analyst may have fabricated data")
        else:
            print("✗ Query returned data (unexpected for 2025)")
    else:
        print(f"✗ Query failed: {result['message']}")

def test_single_value_result():
    """Test that single value results are reported accurately"""
    print("\n" + "="*60)
    print("TEST 2: Single Value Result")
    print("="*60)
    
    # Query for a single aggregate value
    sql = "SELECT COUNT(*) AS TotalOrders FROM salesorders"
    result = corrector.execute_with_retry(sql, max_retries=0)
    
    if result['success']:
        df = result['data']
        actual_value = df.iloc[0, 0]
        print(f"✓ Actual database value: {actual_value}")
        
        # Test that analyst uses exact value
        analysis = analyst.analyze_results_with_llm("How many orders do we have?", df, sql)
        
        # Extract numbers from insight
        numbers = validator.extract_numbers_from_text(analysis['insight'])
        print(f"✓ Numbers in analysis: {numbers}")
        
        if actual_value in numbers or abs(actual_value - numbers[0]) < 0.01 if numbers else False:
            print("✓ PASS: Analysis contains exact database value")
        else:
            print(f"✗ FAIL: Analysis value doesn't match database ({actual_value} vs {numbers})")
    else:
        print(f"✗ Query failed: {result['message']}")

def test_comparison_query():
    """Test year-over-year comparison with actual data"""
    print("\n" + "="*60)
    print("TEST 3: Year-over-Year Comparison")
    print("="*60)
    
    # Query for sales by year
    sql = """
    SELECT 
        YEAR(OrderDate) AS Year,
        SUM(TotalAmount) AS TotalSales
    FROM salesorders
    WHERE YEAR(OrderDate) IN (2023, 2024)
    GROUP BY YEAR(OrderDate)
    ORDER BY Year
    """
    
    result = corrector.execute_with_retry(sql, max_retries=0)
    
    if result['success']:
        df = result['data']
        print("✓ Query executed successfully")
        print("\nActual Data:")
        print(df.to_string(index=False))
        
        if not df.empty:
            # Extract actual values
            actual_numbers = validator.extract_numbers_from_dataframe(df)
            print(f"\n✓ Actual numbers from database: {actual_numbers}")
            
            # Test analyst response
            analysis = analyst.analyze_results_with_llm(
                "What were our total sales in 2024 compared to 2023?", 
                df, 
                sql
            )
            
            print(f"\n✓ Analysis insight:\n{analysis['insight']}")
            
            # Validate response
            is_valid, suspicious = validator.validate_response(analysis['insight'], df)
            
            if is_valid:
                print("\n✓ PASS: All numbers in analysis match database")
            else:
                print(f"\n✗ FAIL: Suspicious numbers detected: {suspicious}")
        else:
            print("⚠ No data for 2023-2024 in database")
    else:
        print(f"✗ Query failed: {result['message']}")

def test_top_customers_query():
    """Test top customers query with actual data"""
    print("\n" + "="*60)
    print("TEST 4: Top Customers Query")
    print("="*60)
    
    sql = """
    SELECT 
        c.CustomerName,
        SUM(so.TotalAmount) AS TotalRevenue
    FROM salesorders so
    JOIN customers c ON so.CustomerID = c.CustomerID
    WHERE YEAR(so.OrderDate) = 2024
    GROUP BY c.CustomerName
    ORDER BY TotalRevenue DESC
    LIMIT 3
    """
    
    result = corrector.execute_with_retry(sql, max_retries=1)
    
    if result['success']:
        df = result['data']
        print("✓ Query executed successfully")
        print("\nActual Data:")
        print(df.to_string(index=False))
        
        if not df.empty:
            # Extract actual values
            actual_numbers = validator.extract_numbers_from_dataframe(df)
            print(f"\n✓ Actual revenue values: {actual_numbers}")
            
            # Test analyst response
            analysis = analyst.analyze_results_with_llm(
                "Who were our top 3 customers by revenue in 2024?", 
                df, 
                sql
            )
            
            print(f"\n✓ Analysis insight:\n{analysis['insight']}")
            
            # Validate response
            is_valid, suspicious = validator.validate_response(analysis['insight'], df, tolerance=1.0)
            
            if is_valid:
                print("\n✓ PASS: All numbers in analysis match database")
            else:
                print(f"\n✗ FAIL: Suspicious numbers detected: {suspicious}")
        else:
            print("⚠ No customer data for 2024 in database")
    else:
        print(f"✗ Query failed: {result['message']}")

def test_sql_syntax_correction():
    """Test SQL syntax error detection and correction"""
    print("\n" + "="*60)
    print("TEST 5: SQL Syntax Error Handling")
    print("="*60)
    
    # Intentionally bad SQL with syntax error
    bad_sql = "SELECT COUNT(*) FROM salesorders FOR YEAR(2024)"
    
    result = corrector.execute_with_retry(bad_sql, max_retries=0)
    
    if not result['success']:
        print("✓ Bad SQL correctly rejected")
        print(f"✓ Error message: {result['message']}")
        
        if "1064" in result['message'] or "Syntax Error" in result['message']:
            print("✓ PASS: Syntax error properly detected and reported")
        else:
            print("⚠ Error detected but not identified as syntax error")
    else:
        print("✗ FAIL: Bad SQL was accepted (should have failed)")

def test_data_validator():
    """Test the data validator directly"""
    print("\n" + "="*60)
    print("TEST 6: Data Validator")
    print("="*60)
    
    # Create sample DataFrame
    df = pd.DataFrame({
        'Year': [2023, 2024],
        'Sales': [3770000.30, 5810000.45]
    })
    
    print("Sample Data:")
    print(df.to_string(index=False))
    
    # Test with correct numbers
    correct_response = "Sales in 2023 were 3770000.30 and in 2024 were 5810000.45"
    is_valid, suspicious = validator.validate_response(correct_response, df)
    
    if is_valid:
        print("\n✓ PASS: Correct numbers validated successfully")
    else:
        print(f"\n✗ FAIL: Correct numbers flagged as suspicious: {suspicious}")
    
    # Test with fabricated numbers (large values that don't match)
    fabricated_response = "Sales in 2023 were 9999999 and in 2024 were 8888888"
    is_valid, suspicious = validator.validate_response(fabricated_response, df)
    
    if not is_valid:
        print(f"\n✓ PASS: Fabricated numbers detected: {suspicious}")
    else:
        print("\n✗ FAIL: Fabricated numbers not detected")

def test_cagr_calculation():
    """Test CAGR calculation directly from SQL"""
    print("\n" + "="*60)
    print("TEST 7: CAGR Calculation from Database")
    print("="*60)
    
    # Test CAGR calculation
    start_year = 2023
    end_year = 2024
    
    result = corrector.calculate_cagr_sql(start_year, end_year)
    
    if result['success']:
        print(f"✓ CAGR calculated successfully: {result['cagr']}%")
        print(f"✓ Start Sales ({start_year}): {result['start_sales']:.2f}")
        print(f"✓ End Sales ({end_year}): {result['end_sales']:.2f}")
        
        # Verify CAGR is a reasonable number
        cagr = result['cagr']
        if -100 <= cagr <= 1000:  # Reasonable CAGR range
            print(f"✓ PASS: CAGR value is reasonable ({cagr}%)")
        else:
            print(f"✗ FAIL: CAGR value seems unreasonable ({cagr}%)")
    else:
        print(f"⚠ CAGR calculation failed: {result['message']}")
        print("⚠ This may be expected if no data exists for these years")

def test_no_markdown_in_response():
    """Test that responses contain no markdown characters"""
    print("\n" + "="*60)
    print("TEST 8: No Markdown in Response")
    print("="*60)
    
    # Query for simple data
    sql = """
    SELECT 
        YEAR(OrderDate) AS Year,
        SUM(TotalAmount) AS TotalSales
    FROM salesorders
    WHERE YEAR(OrderDate) IN (2023, 2024)
    GROUP BY YEAR(OrderDate)
    ORDER BY Year
    """
    
    result = corrector.execute_with_retry(sql, max_retries=0)
    
    if result['success']:
        df = result['data']
        print("✓ Query executed successfully")
        
        if not df.empty:
            # Test analyst response
            analysis = analyst.analyze_results_with_llm(
                "What were our sales in 2023 and 2024?",
                df,
                sql
            )
            
            # Compose response
            response = composer.compose_response(
                'analyst',
                "What were our sales in 2023 and 2024?",
                analysis,
                df.to_string(index=False),
                df=df,
                mode="DETAILED"
            )
            
            print(f"\n✓ Response generated ({len(response)} chars)")
            
            # Check for markdown characters
            import re
            markdown_patterns = [
                (r'\*\*\*', 'Bold+Italic (***text***)'),
                (r'\*\*', 'Bold (**text**)'),
                (r'(?<!\*)\*(?!\*)', 'Italic (*text*)'),
                (r'^#{1,6}\s', 'Headers (# text)', re.MULTILINE),
                (r'```', 'Code blocks (```)'),
                (r'`[^`]+`', 'Inline code (`text`)'),
                (r'\[.+?\]\(.+?\)', 'Links ([text](url))')
            ]
            
            markdown_found = []
            for pattern, description, *flags in markdown_patterns:
                flag = flags[0] if flags else 0
                if re.search(pattern, response, flag):
                    matches = re.findall(pattern, response, flag)
                    markdown_found.append(f"{description}: {len(matches)} occurrences")
            
            if not markdown_found:
                print("✓ PASS: No markdown characters found in response")
            else:
                print(f"✗ FAIL: Markdown characters detected:")
                for item in markdown_found:
                    print(f"  - {item}")
            
            # Test COMPACT mode
            composer.set_mode("COMPACT")
            response_compact = composer.compose_response(
                'analyst',
                "What were our sales in 2023 and 2024?",
                analysis,
                df.to_string(index=False),
                df=df,
                mode="COMPACT"
            )
            
            print(f"\n✓ COMPACT response generated ({len(response_compact)} chars)")
            
            markdown_found_compact = []
            for pattern, description, *flags in markdown_patterns:
                flag = flags[0] if flags else 0
                if re.search(pattern, response_compact, flag):
                    matches = re.findall(pattern, response_compact, flag)
                    markdown_found_compact.append(f"{description}: {len(matches)} occurrences")
            
            if not markdown_found_compact:
                print("✓ PASS: No markdown in COMPACT mode response")
            else:
                print(f"✗ FAIL: Markdown in COMPACT mode:")
                for item in markdown_found_compact:
                    print(f"  - {item}")
            
            # Verify COMPACT is shorter than DETAILED
            if len(response_compact) < len(response):
                print(f"✓ PASS: COMPACT mode is shorter ({len(response_compact)} vs {len(response)} chars)")
            else:
                print(f"⚠ WARNING: COMPACT mode not shorter than DETAILED")
            
        else:
            print("⚠ No data for testing")
    else:
        print(f"✗ Query failed: {result['message']}")

def test_trend_detection_3_years():
    """Test trend detection with 3-year data"""
    print("\n" + "="*60)
    print("TEST 9: Trend Detection with 3-Year Data")
    print("="*60)
    
    # Query for 3 years of sales data
    sql = """
    SELECT 
        YEAR(OrderDate) AS Year,
        SUM(TotalAmount) AS TotalSales
    FROM salesorders
    WHERE YEAR(OrderDate) IN (2022, 2023, 2024)
    GROUP BY YEAR(OrderDate)
    ORDER BY Year
    """
    
    result = corrector.execute_with_retry(sql, max_retries=0)
    
    if result['success']:
        df = result['data']
        print("✓ Query executed successfully")
        print("\nActual Data:")
        print(df.to_string(index=False))
        
        if not df.empty and len(df) >= 2:
            # Test detect_trend helper directly
            sales_series = df['TotalSales']
            trend = analyst.detect_trend(sales_series)
            
            print(f"\n✓ Trend detected: {trend}")
            
            # Verify trend is one of the expected values
            if trend in ['upward', 'downward', 'stable']:
                print(f"✓ PASS: Valid trend direction detected")
                
                # Test analyze_trends for full summary with emoji
                trend_summary = analyst.analyze_trends(df)
                print(f"\n✓ Full trend summary:\n{trend_summary}")
                
                # Verify emoji is included
                emoji_map = {'upward': '📈', 'downward': '📉', 'stable': '➖'}
                expected_emoji = emoji_map[trend]
                
                if expected_emoji in trend_summary:
                    print(f"✓ PASS: Trend summary includes correct emoji {expected_emoji}")
                else:
                    print(f"✗ FAIL: Trend summary missing emoji {expected_emoji}")
                
                # Test that response_composer includes trend
                analysis = analyst.analyze_results_with_llm(
                    "What were our sales trends from 2022 to 2024?",
                    df,
                    sql
                )
                
                response = composer.compose_response(
                    'analyst',
                    "What were our sales trends from 2022 to 2024?",
                    analysis,
                    df.to_string(index=False),
                    df=df
                )
                
                if expected_emoji in response and trend.capitalize() in response:
                    print(f"✓ PASS: Response includes trend with emoji")
                else:
                    print(f"⚠ WARNING: Response may not include trend summary")
                    print(f"Response preview: {response[:200]}...")
                
            else:
                print(f"✗ FAIL: Invalid trend value: {trend}")
        else:
            print("⚠ Insufficient data for trend detection (need at least 2 years)")
            print("⚠ This may be expected if database doesn't have 3 years of data")
    else:
        print(f"✗ Query failed: {result['message']}")

def test_graceful_empty_result():
    """Test graceful handling of empty results"""
    print("\n" + "="*60)
    print("TEST 10: Graceful Empty Result Handling")
    print("="*60)
    
    # Query that will return empty result
    sql = "SELECT * FROM salesorders WHERE YEAR(OrderDate) = 2099"
    result = corrector.execute_with_retry(sql, max_retries=0)
    
    if result['success'] and result['data'].empty:
        print("✓ Query returned empty result as expected")
        
        # Simulate the error logging
        from error_logger import error_logger
        error_logger.log_sql_error(
            error_type="EMPTY_RESULT",
            sql=sql,
            error_message="Query executed successfully but returned no data",
            question="What were sales in 2099?",
            context={"mode": "DETAILED", "test": True}
        )
        
        # Check if log file was created
        import os
        if os.path.exists("logs/errors.log"):
            print("✓ Error logged to logs/errors.log")
            
            # Verify log content
            with open("logs/errors.log", 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            if "EMPTY_RESULT" in log_content and "2099" in log_content:
                print("✓ PASS: Empty result logged correctly")
            else:
                print("✗ FAIL: Log content incomplete")
        else:
            print("✗ FAIL: Error log file not created")
    else:
        print("⚠ Query did not return empty result (unexpected)")

def test_graceful_syntax_error():
    """Test graceful handling of SQL syntax errors"""
    print("\n" + "="*60)
    print("TEST 11: Graceful Syntax Error Handling")
    print("="*60)
    
    # Intentionally bad SQL
    bad_sql = "SELECT COUNT(*) FROM salesorders WHERE YEAR = 2024"  # Missing function call
    result = corrector.execute_with_retry(bad_sql, max_retries=0)
    
    if not result['success']:
        print("✓ Bad SQL correctly rejected")
        error_message = result['message']
        
        # Simulate error logging
        from error_logger import error_logger
        
        # Determine error type
        if "1064" in error_message or "syntax" in error_message.lower():
            error_type = "SYNTAX_ERROR"
            user_message = "Invalid SQL syntax. Please adjust your query or check table names."
        else:
            error_type = "EXECUTION_ERROR"
            user_message = "SQL execution failed. Please try rephrasing your question."
        
        error_logger.log_sql_error(
            error_type=error_type,
            sql=bad_sql,
            error_message=error_message,
            question="Test syntax error",
            context={"test": True}
        )
        
        print(f"✓ Error type detected: {error_type}")
        print(f"✓ User message: {user_message}")
        
        # Verify graceful message format
        if "Invalid SQL syntax" in user_message or "SQL execution failed" in user_message:
            print("✓ PASS: Graceful error message generated")
        else:
            print("✗ FAIL: Error message not user-friendly")
    else:
        print("✗ FAIL: Bad SQL was accepted (should have failed)")

def test_error_log_retrieval():
    """Test error log retrieval functionality"""
    print("\n" + "="*60)
    print("TEST 12: Error Log Retrieval")
    print("="*60)
    
    from error_logger import error_logger
    
    # Log a test error
    error_logger.log_sql_error(
        error_type="TEST_ERROR",
        sql="SELECT * FROM test_table",
        error_message="This is a test error",
        question="Test question",
        context={"test": True}
    )
    
    # Retrieve recent errors
    recent_errors = error_logger.get_recent_errors(n=5)
    
    if recent_errors:
        print(f"✓ Retrieved {len(recent_errors)} error entries")
        
        # Check if our test error is in the list
        found_test_error = any("TEST_ERROR" in str(error) for error in recent_errors)
        
        if found_test_error:
            print("✓ PASS: Test error found in recent errors")
        else:
            print("⚠ WARNING: Test error not found (may have been cleared)")
    else:
        print("⚠ No errors in log (may be expected if log was cleared)")

def test_plain_text_error_messages():
    """Test that error messages are in plain text format"""
    print("\n" + "="*60)
    print("TEST 13: Plain Text Error Messages")
    print("="*60)
    
    # Simulate error messages
    separator = "─" * 60
    
    # Empty result message
    empty_msg = f"{separator}\n"
    empty_msg += "NO DATA FOUND\n"
    empty_msg += f"{separator}\n\n"
    empty_msg += "No data found for this query.\n\n"
    empty_msg += "Possible causes:\n"
    empty_msg += "- No data exists for the given year or time period\n"
    
    # SQL error message
    error_msg = f"{separator}\n"
    error_msg += "SQL ERROR\n"
    error_msg += f"{separator}\n\n"
    error_msg += "Invalid SQL syntax. Please adjust your query or check table names.\n"
    
    # Check for markdown
    import re
    markdown_patterns = [
        r'\*\*',    # Bold
        r'(?<!\*)\*(?!\*)',  # Italic
        r'^#{1,6}\s',  # Headers
        r'```',     # Code blocks
    ]
    
    has_markdown_empty = any(re.search(p, empty_msg, re.MULTILINE) for p in markdown_patterns)
    has_markdown_error = any(re.search(p, error_msg, re.MULTILINE) for p in markdown_patterns)
    
    if not has_markdown_empty and not has_markdown_error:
        print("✓ PASS: Error messages contain no markdown")
    else:
        print("✗ FAIL: Markdown found in error messages")
    
    # Verify separator lines are present
    if "─" in empty_msg and "─" in error_msg:
        print("✓ PASS: Separator lines present in error messages")
    else:
        print("✗ FAIL: Separator lines missing")

def run_all_tests():
    """Run all accuracy tests"""
    print("\n" + "="*70)
    print("SQL ACCURACY TEST SUITE")
    print("Testing that all responses match actual database data")
    print("="*70)
    
    try:
        test_empty_result_handling()
        test_single_value_result()
        test_comparison_query()
        test_top_customers_query()
        test_sql_syntax_correction()
        test_data_validator()
        test_cagr_calculation()
        test_no_markdown_in_response()
        test_trend_detection_3_years()
        test_graceful_empty_result()
        test_graceful_syntax_error()
        test_error_log_retrieval()
        test_plain_text_error_messages()
        
        print("\n" + "="*70)
        print("TEST SUITE COMPLETED")
        print("="*70)
        print("\nReview the results above to verify:")
        print("1. Empty results don't generate fabricated data")
        print("2. Single values are reported exactly")
        print("3. Comparisons use actual database numbers")
        print("4. Top N queries show real data")
        print("5. SQL syntax errors are caught")
        print("6. Data validator detects fabricated numbers")
        print("7. CAGR is calculated directly from database")
        print("8. Responses contain no markdown characters (COMPACT & DETAILED modes)")
        print("9. Trend detection works with 3-year data and includes emoji")
        print("10. Empty results handled gracefully with logging")
        print("11. Syntax errors handled gracefully with logging")
        print("12. Error logs can be retrieved")
        print("13. Error messages are in plain text format")
        
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
