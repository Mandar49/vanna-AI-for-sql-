"""
CAGR Calculation Demo
Demonstrates the SQL-based CAGR calculation with zero fabrication
"""
from sql_corrector import corrector
from business_analyst import analyst

def demo_cagr_calculation():
    """Demonstrate CAGR calculation"""
    print("\n" + "="*70)
    print("CAGR CALCULATION DEMO")
    print("="*70)
    print("\nThis demo shows how CAGR is calculated directly from SQL")
    print("with zero LLM fabrication or computation.\n")
    
    # Example 1: Calculate CAGR for 2023-2024
    print("-" * 70)
    print("EXAMPLE 1: CAGR from 2023 to 2024")
    print("-" * 70)
    
    result = corrector.calculate_cagr_sql(2023, 2024)
    
    if result['success']:
        print(f"\n✓ Calculation successful!")
        print(f"\n📊 Results (Direct from Database):")
        print(f"   CAGR: {result['cagr']}%")
        print(f"   Period: {result['start_year']} to {result['end_year']}")
        print(f"   Starting Sales: ${result['start_sales']:,.2f}")
        print(f"   Ending Sales: ${result['end_sales']:,.2f}")
        
        # Show the calculation
        print(f"\n🔢 Calculation:")
        print(f"   CAGR = (Ending / Starting)^(1/Years) - 1")
        print(f"   CAGR = ({result['end_sales']:.2f} / {result['start_sales']:.2f})^(1/1) - 1")
        print(f"   CAGR = {result['end_sales']/result['start_sales']:.6f} - 1")
        print(f"   CAGR = {(result['end_sales']/result['start_sales']) - 1:.6f}")
        print(f"   CAGR = {result['cagr']}%")
        
        print(f"\n💡 All numbers above are from the actual database.")
    else:
        print(f"\n✗ Calculation failed: {result['message']}")
    
    # Example 2: Query detection
    print("\n" + "-" * 70)
    print("EXAMPLE 2: Query Detection")
    print("-" * 70)
    
    test_queries = [
        "What is the CAGR from 2023 to 2024?",
        "Calculate compound annual growth rate 2022-2024",
        "Show me the annual growth between 2023 and 2024",
        "What were sales in 2024?"  # Should NOT be detected
    ]
    
    print("\nTesting query detection:")
    for query in test_queries:
        detected = analyst.detect_cagr_query(query)
        years = analyst.extract_years_from_query(query)
        
        print(f"\n   Query: '{query}'")
        print(f"   Detected as CAGR: {detected}")
        if detected and years[0]:
            print(f"   Years extracted: {years[0]} to {years[1]}")
    
    # Example 3: Full response
    print("\n" + "-" * 70)
    print("EXAMPLE 3: Full Response Format")
    print("-" * 70)
    
    print("\nWhen you ask: 'What is the CAGR from 2023 to 2024?'")
    print("\nYou will see:")
    print("""
✅ SQL Result:
Year  TotalSales
2023  3996499.31
2024  4110315.23

📊 CAGR (Direct from Database): 2.85%
Period: 2023 to 2024
Starting Sales: 3996499.31
Ending Sales: 4110315.23

📊 CAGR Analysis (Direct from Database):

**CAGR:** 2.85%
**Period:** 2023 to 2024
**Starting Sales:** 3996499.31
**Ending Sales:** 4110315.23

**Insight:** The Compound Annual Growth Rate (CAGR) from 2023 to 2024 is 2.85%. 
Sales grew from 3996499.31 in 2023 to 4110315.23 in 2024.

**Recommendations:**
- The 2.85% CAGR indicates slow growth over this period.
- Monitor this growth rate against industry benchmarks.
- Analyze factors contributing to this growth trajectory.

💡 All numbers above are calculated directly from the database.
    """)
    
    print("\n" + "="*70)
    print("KEY FEATURES")
    print("="*70)
    print("""
✓ CAGR calculated directly in SQL (no LLM computation)
✓ Uses database POWER function for accuracy
✓ All intermediate values shown (start, end, period)
✓ Automatic detection from natural language queries
✓ Complete transparency with SQL query display
✓ Zero fabrication or hallucination
✓ 100% verifiable results
    """)
    
    print("\n" + "="*70)
    print("TRY IT YOURSELF")
    print("="*70)
    print("""
1. Start the application:
   python ad_ai_app.py

2. Open your browser:
   http://127.0.0.1:5000

3. Ask any of these questions:
   - "What is the CAGR from 2023 to 2024?"
   - "Calculate the compound annual growth rate from 2022 to 2024"
   - "Show me the annual growth rate between 2023 and 2024"

4. Verify the response:
   - CAGR percentage is shown
   - Start and end sales are displayed
   - All values match the database
   - "Direct from Database" note is included
    """)

if __name__ == "__main__":
    demo_cagr_calculation()
