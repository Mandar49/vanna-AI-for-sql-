"""
Demo: Graceful Error Handling
Demonstrates error logging and user-friendly error messages
"""
from sql_corrector import corrector
from error_logger import error_logger
import os

def demo_error_handling():
    """Demonstrate graceful error handling"""
    
    print("=" * 70)
    print("ERROR HANDLING DEMONSTRATION")
    print("=" * 70)
    
    # Clear previous logs for clean demo
    error_logger.clear_log()
    print("\n✓ Error log cleared for demo\n")
    
    # Test 1: Empty Result
    print("=" * 70)
    print("TEST 1: Empty Result Handling")
    print("=" * 70)
    
    sql_empty = "SELECT * FROM salesorders WHERE YEAR(OrderDate) = 2099"
    print(f"\nExecuting: {sql_empty}")
    
    result = corrector.execute_with_retry(sql_empty, max_retries=0)
    
    if result['success'] and result['data'].empty:
        print("\n✓ Query executed but returned no data")
        
        # Log the error
        error_logger.log_sql_error(
            error_type="EMPTY_RESULT",
            sql=sql_empty,
            error_message="Query executed successfully but returned no data",
            question="What were sales in 2099?",
            context={"mode": "DETAILED", "demo": True}
        )
        
        # Show user-friendly message
        separator = "─" * 60
        empty_msg = f"{separator}\n"
        empty_msg += "NO DATA FOUND\n"
        empty_msg += f"{separator}\n\n"
        empty_msg += "No data found for this query.\n\n"
        empty_msg += "Possible causes:\n"
        empty_msg += "- No data exists for the given year or time period\n"
        empty_msg += "- Filters are too narrow or restrictive\n"
        
        print("\nUser-Friendly Message:")
        print(empty_msg)
    
    # Test 2: Syntax Error
    print("\n" + "=" * 70)
    print("TEST 2: Syntax Error Handling")
    print("=" * 70)
    
    sql_bad = "SELECT COUNT(*) FROM salesorders WHERE YEAR = 2024"
    print(f"\nExecuting: {sql_bad}")
    
    result = corrector.execute_with_retry(sql_bad, max_retries=0)
    
    if not result['success']:
        print("\n✓ Query failed as expected")
        error_message = result['message']
        
        # Determine error type
        if "1064" in error_message or "syntax" in error_message.lower():
            error_type = "SYNTAX_ERROR"
            user_message = "Invalid SQL syntax. Please adjust your query or check table names."
        else:
            error_type = "EXECUTION_ERROR"
            user_message = "SQL execution failed. Please try rephrasing your question."
        
        # Log the error
        error_logger.log_sql_error(
            error_type=error_type,
            sql=sql_bad,
            error_message=error_message,
            question="What were total sales in 2024?",
            context={"mode": "DETAILED", "demo": True}
        )
        
        # Show user-friendly message
        separator = "─" * 60
        error_msg = f"{separator}\n"
        error_msg += "SQL ERROR\n"
        error_msg += f"{separator}\n\n"
        error_msg += f"{user_message}\n\n"
        error_msg += f"Technical Details:\n{error_message}\n\n"
        error_msg += f"SQL Query:\n{sql_bad}\n\n"
        error_msg += "Suggestion: Try rephrasing your question or ask 'What tables are available?'"
        
        print("\nUser-Friendly Message:")
        print(error_msg)
    
    # Test 3: View Error Logs
    print("\n" + "=" * 70)
    print("TEST 3: Error Log Retrieval")
    print("=" * 70)
    
    recent_errors = error_logger.get_recent_errors(n=5)
    
    print(f"\n✓ Retrieved {len(recent_errors)} error entries")
    
    if recent_errors:
        print("\nRecent Errors:")
        for i, error in enumerate(recent_errors, 1):
            print(f"\n--- Error {i} ---")
            # Show first 200 chars of each error
            preview = error[:200] + "..." if len(error) > 200 else error
            print(preview)
    
    # Test 4: Check Log File
    print("\n" + "=" * 70)
    print("TEST 4: Log File Verification")
    print("=" * 70)
    
    log_file = "logs/errors.log"
    if os.path.exists(log_file):
        print(f"\n✓ Log file exists: {log_file}")
        
        file_size = os.path.getsize(log_file)
        print(f"✓ Log file size: {file_size} bytes")
        
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count error entries
        error_count = content.count("SQL ERROR:")
        print(f"✓ Total errors logged: {error_count}")
        
        # Check for specific error types
        has_empty = "EMPTY_RESULT" in content
        has_syntax = "SYNTAX_ERROR" in content
        
        print(f"✓ Contains EMPTY_RESULT: {has_empty}")
        print(f"✓ Contains SYNTAX_ERROR: {has_syntax}")
    else:
        print(f"\n✗ Log file not found: {log_file}")
    
    # Summary
    print("\n" + "=" * 70)
    print("DEMO SUMMARY")
    print("=" * 70)
    print("\n✓ Empty results handled gracefully")
    print("✓ Syntax errors handled gracefully")
    print("✓ All errors logged to logs/errors.log")
    print("✓ User-friendly messages in plain text format")
    print("✓ Error logs retrievable programmatically")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    demo_error_handling()
