"""
Forecast Demo - Complete Numeric Determinism
Demonstrates SQL-based forecasting with zero LLM estimation
"""
from sql_corrector import corrector
from data_validator import validator

def demo_forecast_calculation():
    """Demonstrate forecast calculation with scenarios"""
    print("\n" + "="*70)
    print("FORECAST CALCULATION DEMO")
    print("="*70)
    print("\nThis demo shows complete numeric determinism:")
    print("- CAGR calculated in SQL")
    print("- Forecasts calculated with exact formulas")
    print("- Scenarios mathematically derived")
    print("- Strict validation enforced\n")
    
    # Example: Forecast for 2025 and 2026
    print("-" * 70)
    print("EXAMPLE: Forecast Sales for 2025 and 2026")
    print("-" * 70)
    
    start_year = 2023
    end_year = 2024
    forecast_years = [2025, 2026]
    
    result = corrector.calculate_cagr_sql(start_year, end_year, forecast_years)
    
    if result['success']:
        print(f"\n[OK] Calculation successful!")
        
        # Show CAGR
        print(f"\n[CAGR] (Direct from Database):")
        print(f"   Period: {result['start_year']} to {result['end_year']}")
        print(f"   CAGR: {result['cagr']}%")
        print(f"   Starting Sales: ${result['start_sales']:,.2f}")
        print(f"   Ending Sales: ${result['end_sales']:,.2f}")
        
        # Validate CAGR
        is_valid, msg = validator.validate_cagr(
            result['cagr'],
            result['start_sales'],
            result['end_sales'],
            start_year,
            end_year
        )
        print(f"\n[VALIDATION] {msg}")
        
        # Show forecasts
        print(f"\n[FORECASTS]:")
        for year in sorted(result['forecast'].keys()):
            print(f"\n   {year}:")
            
            if year in result['scenarios']:
                scenarios = result['scenarios'][year]
                print(f"      Base (CAGR {scenarios['cagr_base']}%): ${scenarios['base']:,.2f}")
                print(f"      Optimistic (+10%, CAGR {scenarios['cagr_optimistic']}%): ${scenarios['optimistic']:,.2f}")
                print(f"      Pessimistic (-10%, CAGR {scenarios['cagr_pessimistic']}%): ${scenarios['pessimistic']:,.2f}")
                
                # Validate forecast
                years_ahead = year - end_year
                is_valid, msg = validator.validate_forecast(
                    scenarios['base'],
                    result['end_sales'],
                    result['cagr_decimal'],
                    years_ahead
                )
                print(f"      [VALIDATION] {msg}")
        
        # Show formulas
        print(f"\n[FORMULAS] Used:")
        print(f"   CAGR = ((End/Start)^(1/Years) - 1) * 100")
        print(f"   CAGR = (({result['end_sales']:.2f}/{result['start_sales']:.2f})^(1/1) - 1) * 100")
        print(f"   CAGR = {result['cagr']}%")
        
        print(f"\n   Forecast = Base * (1 + CAGR)^YearsAhead")
        print(f"   2025 = {result['end_sales']:.2f} * (1 + {result['cagr_decimal']:.4f})^1")
        print(f"   2025 = ${result['forecast'][2025]:,.2f}")
        
        print(f"\n[NOTE] All numbers above are calculated directly from the database.")
        
    else:
        print(f"\n[ERROR] Calculation failed: {result['message']}")

def demo_scenario_analysis():
    """Demonstrate scenario analysis"""
    print("\n" + "-" * 70)
    print("SCENARIO ANALYSIS")
    print("-" * 70)
    
    start_year = 2023
    end_year = 2024
    forecast_years = [2025]
    
    result = corrector.calculate_cagr_sql(start_year, end_year, forecast_years)
    
    if result['success'] and 2025 in result['scenarios']:
        scenarios = result['scenarios'][2025]
        
        print(f"\nBase CAGR: {result['cagr']}%")
        print(f"Base Sales (2024): ${result['end_sales']:,.2f}")
        
        print(f"\n[SCENARIOS] 2025:")
        print(f"\n   1. Optimistic (+10% CAGR):")
        print(f"      CAGR: {scenarios['cagr_optimistic']}%")
        print(f"      Forecast: ${scenarios['optimistic']:,.2f}")
        print(f"      Formula: {result['end_sales']:.2f} * (1 + {result['cagr_decimal']*1.10:.4f})^1")
        
        print(f"\n   2. Base (Actual CAGR):")
        print(f"      CAGR: {scenarios['cagr_base']}%")
        print(f"      Forecast: ${scenarios['base']:,.2f}")
        print(f"      Formula: {result['end_sales']:.2f} * (1 + {result['cagr_decimal']:.4f})^1")
        
        print(f"\n   3. Pessimistic (-10% CAGR):")
        print(f"      CAGR: {scenarios['cagr_pessimistic']}%")
        print(f"      Forecast: ${scenarios['pessimistic']:,.2f}")
        print(f"      Formula: {result['end_sales']:.2f} * (1 + {result['cagr_decimal']*0.90:.4f})^1")
        
        # Show range
        range_amount = scenarios['optimistic'] - scenarios['pessimistic']
        range_percent = (range_amount / scenarios['base']) * 100
        
        print(f"\n[RANGE] Forecast Range:")
        print(f"   Low: ${scenarios['pessimistic']:,.2f}")
        print(f"   Mid: ${scenarios['base']:,.2f}")
        print(f"   High: ${scenarios['optimistic']:,.2f}")
        print(f"   Range: ${range_amount:,.2f} ({range_percent:.1f}% of base)")

def demo_validation():
    """Demonstrate strict validation"""
    print("\n" + "-" * 70)
    print("VALIDATION DEMO")
    print("-" * 70)
    
    print("\n[TEST] Validating correct CAGR:")
    is_valid, msg = validator.validate_cagr(2.85, 3996499.31, 4110315.23, 2023, 2024)
    print(f"   {msg}")
    print(f"   Result: {'PASS' if is_valid else 'FAIL'}")
    
    print("\n[TEST] Validating fabricated CAGR:")
    is_valid, msg = validator.validate_cagr(5.0, 3996499.31, 4110315.23, 2023, 2024)
    print(f"   {msg}")
    print(f"   Result: {'REJECTED (correct)' if not is_valid else 'ACCEPTED (wrong)'}")
    
    print("\n[TEST] Validating correct forecast:")
    is_valid, msg = validator.validate_forecast(4227372.50, 4110315.23, 0.0285, 1)
    print(f"   {msg}")
    print(f"   Result: {'PASS' if is_valid else 'FAIL'}")
    
    print("\n[TEST] Validating fabricated forecast:")
    is_valid, msg = validator.validate_forecast(5000000.0, 4110315.23, 0.0285, 1)
    print(f"   {msg}")
    print(f"   Result: {'REJECTED (correct)' if not is_valid else 'ACCEPTED (wrong)'}")
    
    print("\n[NOTE] Validation ensures:")
    print("   - CAGR accuracy: +/-0.01%")
    print("   - Forecast accuracy: +/-Rs.1.00")
    print("   - No LLM fabrication or estimation")

def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("COMPLETE NUMERIC DETERMINISM DEMO")
    print("="*70)
    print("\nDemonstrating:")
    print("1. Forecast calculation with scenarios")
    print("2. Scenario analysis (Optimistic/Base/Pessimistic)")
    print("3. Strict validation enforcement")
    
    try:
        demo_forecast_calculation()
        demo_scenario_analysis()
        demo_validation()
        
        print("\n" + "="*70)
        print("KEY FEATURES")
        print("="*70)
        print("""
[OK] CAGR calculated directly in SQL (no LLM computation)
[OK] Forecasts calculated with exact mathematical formulas
[OK] Scenarios mathematically derived (+10% / Base / -10%)
[OK] Strict validation (CAGR +/-0.01%, Forecast +/-Rs.1.00)
[OK] Complete transparency with all formulas shown
[OK] Zero fabrication or hallucination
[OK] 100% verifiable results
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
   - "Forecast sales for 2025 based on 2023-2024 trend"
   - "Project revenue for 2025 and 2026"
   - "What will sales be in 2025?"
   - "Predict future sales with scenarios"

4. Verify the response:
   - CAGR percentage is shown
   - Forecasts for requested years
   - Three scenarios (Base/Optimistic/Pessimistic)
   - All values match formulas
   - "Direct from Database" note included

5. Test the API:
   curl -X POST http://localhost:5000/api/forecast \\
     -H "Content-Type: application/json" \\
     -d '{"start_year": 2023, "end_year": 2024, "forecast_years": [2025, 2026]}'
        """)
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
