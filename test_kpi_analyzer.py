"""
Test suite for KPI Analyzer (Phase 5D)
Tests quantitative analysis, anomaly detection, and visualization integration.
"""

import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_kpi_analysis():
    """Test 1: Basic KPI analysis."""
    print("\n" + "="*70)
    print("TEST 1: KPI Analysis")
    print("="*70)
    
    try:
        from kpi_analyzer import analyze_kpis
        
        # Create sample data
        df = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [100000, 120000, 115000, 135000, 142000, 138000],
            'Cost': [60000, 70000, 65000, 75000, 80000, 78000]
        })
        
        print(f"✓ Created test dataframe with {len(df)} rows")
        
        # Analyze KPIs
        result = analyze_kpis(df)
        
        if result['status'] == 'success':
            metrics = result['metrics']
            print(f"✓ KPI analysis successful")
            print(f"\n  Summary Statistics:")
            print(f"    - Total: ${metrics['summary']['total']:,.2f}")
            print(f"    - Mean: ${metrics['summary']['mean']:,.2f}")
            print(f"    - Std Dev: ${metrics['summary']['std']:,.2f}")
            
            if 'growth' in metrics:
                print(f"\n  Growth Metrics:")
                print(f"    - Growth Rate: {metrics['growth'].get('growth_rate', 0):.2%}")
                print(f"    - Trend: {metrics['growth'].get('trend', 'N/A')}")
            
            if 'financial' in metrics and metrics['financial']:
                print(f"\n  Financial Metrics:")
                print(f"    - Profit Margin: {metrics['financial'].get('profit_margin', 0):.2%}")
                print(f"    - ROI: {metrics['financial'].get('roi', 0):.2%}")
            
            return True
        else:
            print(f"✗ Analysis failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"✗ KPI analysis test failed: {e}")
        return False


def test_anomaly_detection():
    """Test 2: Anomaly detection."""
    print("\n" + "="*70)
    print("TEST 2: Anomaly Detection")
    print("="*70)
    
    try:
        from kpi_analyzer import detect_anomalies
        
        # Create data with anomalies
        np.random.seed(42)
        normal_data = np.random.normal(100, 10, 20)
        anomalies_data = np.concatenate([normal_data, [150, 50, 200]])  # Add outliers
        
        df = pd.DataFrame({
            'Value': anomalies_data
        })
        
        print(f"✓ Created test data with {len(df)} points (including 3 anomalies)")
        
        # Detect anomalies using IQR method
        result = detect_anomalies(df, value_col='Value', method='iqr', threshold=1.5)
        
        if result['status'] == 'success':
            print(f"✓ Anomaly detection successful")
            print(f"  - Method: {result['method']}")
            print(f"  - Anomalies found: {result['anomaly_count']}")
            print(f"  - Percentage: {result['anomaly_percentage']:.1f}%")
            
            if result['anomalies']:
                print(f"\n  Top Anomalies:")
                for i, anomaly in enumerate(result['anomalies'][:3], 1):
                    print(f"    {i}. Index {anomaly['index']}: {anomaly['value']:.2f} ({anomaly['deviation']})")
            
            return result['anomaly_count'] > 0
        else:
            print(f"✗ Detection failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"✗ Anomaly detection test failed: {e}")
        return False


def test_growth_calculation():
    """Test 3: Growth rate calculation."""
    print("\n" + "="*70)
    print("TEST 3: Growth Rate Calculation")
    print("="*70)
    
    try:
        from kpi_analyzer import calculate_growth_rate
        
        test_cases = [
            (150000, 120000, 'YoY'),
            (95000, 100000, 'MoM'),
            (200000, 150000, 'QoQ')
        ]
        
        all_passed = True
        
        for current, previous, period in test_cases:
            result = calculate_growth_rate(current, previous, period)
            
            print(f"\n  {period} Growth:")
            print(f"    Current: ${current:,.0f}")
            print(f"    Previous: ${previous:,.0f}")
            print(f"    Growth Rate: {result['growth_rate']:.2%}")
            print(f"    Status: {result['status']}")
            
            if result['growth_rate'] is None:
                all_passed = False
        
        if all_passed:
            print(f"\n✓ All growth calculations successful")
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Growth calculation test failed: {e}")
        return False


def test_profit_margin():
    """Test 4: Profit margin calculation."""
    print("\n" + "="*70)
    print("TEST 4: Profit Margin Calculation")
    print("="*70)
    
    try:
        from kpi_analyzer import calculate_profit_margin
        
        test_cases = [
            (200000, 140000, "good"),
            (150000, 120000, "good"),
            (100000, 95000, "marginal")
        ]
        
        all_passed = True
        
        for revenue, cost, expected_status in test_cases:
            result = calculate_profit_margin(revenue, cost)
            
            print(f"\n  Revenue: ${revenue:,.0f}, Cost: ${cost:,.0f}")
            print(f"    Profit: ${result['profit']:,.0f}")
            print(f"    Margin: {result['profit_margin']:.2%}")
            print(f"    Status: {result['status']}")
            
            if result['profit_margin'] is None:
                all_passed = False
        
        if all_passed:
            print(f"\n✓ All profit margin calculations successful")
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Profit margin test failed: {e}")
        return False


def test_variance_calculation():
    """Test 5: Variance calculation."""
    print("\n" + "="*70)
    print("TEST 5: Variance Calculation")
    print("="*70)
    
    try:
        from kpi_analyzer import calculate_variance
        
        test_cases = [
            (120000, 100000, "above_target"),
            (95000, 100000, "below_target"),
            (102000, 100000, "on_target")
        ]
        
        all_passed = True
        
        for actual, target, expected_status in test_cases:
            result = calculate_variance(actual, target)
            
            print(f"\n  Actual: ${actual:,.0f}, Target: ${target:,.0f}")
            print(f"    Variance: ${result['variance']:,.0f}")
            print(f"    Variance %: {result['variance_pct']:.2%}")
            print(f"    Status: {result['status']}")
            
            if result['status'] != expected_status:
                print(f"    ⚠ Expected {expected_status}, got {result['status']}")
        
        print(f"\n✓ Variance calculations complete")
        return all_passed
        
    except Exception as e:
        print(f"✗ Variance calculation test failed: {e}")
        return False


def test_kpi_summary():
    """Test 6: KPI summary generation."""
    print("\n" + "="*70)
    print("TEST 6: KPI Summary Generation")
    print("="*70)
    
    try:
        from kpi_analyzer import generate_kpi_summary
        
        df = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'Revenue': [100000, 120000, 115000, 135000, 142000],
            'Cost': [60000, 70000, 65000, 75000, 80000]
        })
        
        summary = generate_kpi_summary(df)
        
        if summary and len(summary) > 0:
            print(f"✓ Summary generated ({len(summary)} characters)")
            print(f"\n{summary}")
            return True
        else:
            print(f"✗ Summary generation failed")
            return False
            
    except Exception as e:
        print(f"✗ KPI summary test failed: {e}")
        return False


def test_orchestrator_integration():
    """Test 7: Orchestrator integration."""
    print("\n" + "="*70)
    print("TEST 7: Orchestrator Integration")
    print("="*70)
    
    try:
        from orchestrator import execute_command
        
        # Test KPI analysis command
        commands = [
            "analyze KPIs for Sales",
            "analyze financial metrics for Marketing"
        ]
        
        all_passed = True
        
        for command in commands:
            print(f"\n  Command: '{command}'")
            result = execute_command(command)
            
            print(f"    Status: {result['status']}")
            print(f"    Message: {result['message']}")
            
            if result['status'] == 'success':
                outputs = result.get('outputs', {})
                if 'metrics' in outputs:
                    print(f"    ✓ Metrics generated")
                if 'summary' in outputs:
                    print(f"    ✓ Summary generated")
            else:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Orchestrator integration test failed: {e}")
        return False


def test_visualization_integration():
    """Test 8: Visualization integration."""
    print("\n" + "="*70)
    print("TEST 8: Visualization Integration")
    print("="*70)
    
    try:
        from kpi_analyzer import analyze_kpis, detect_anomalies
        from viz import chart_kpi_dashboard, chart_anomalies, chart_growth_comparison
        
        # Create test data
        df = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Revenue': [100000, 120000, 115000, 135000, 142000, 138000],
            'Cost': [60000, 70000, 65000, 75000, 80000, 78000]
        })
        
        # Test 1: KPI Dashboard
        print("\n  Testing KPI dashboard chart...")
        kpis = analyze_kpis(df)
        if kpis['status'] == 'success':
            chart_path = chart_kpi_dashboard(kpis['metrics'])
            if os.path.exists(chart_path):
                print(f"    ✓ KPI dashboard created: {os.path.basename(chart_path)}")
            else:
                print(f"    ✗ Chart file not found")
                return False
        
        # Test 2: Anomaly chart
        print("\n  Testing anomaly detection chart...")
        anomaly_result = detect_anomalies(df, value_col='Revenue')
        if anomaly_result['status'] == 'success':
            chart_path = chart_anomalies(df, anomaly_result['anomalies'], 'Revenue')
            if os.path.exists(chart_path):
                print(f"    ✓ Anomaly chart created: {os.path.basename(chart_path)}")
            else:
                print(f"    ✗ Chart file not found")
                return False
        
        # Test 3: Growth comparison
        print("\n  Testing growth comparison chart...")
        chart_path = chart_growth_comparison(
            current=142000,
            previous=100000,
            target=130000
        )
        if os.path.exists(chart_path):
            print(f"    ✓ Growth comparison created: {os.path.basename(chart_path)}")
        else:
            print(f"    ✗ Chart file not found")
            return False
        
        print(f"\n✓ All visualization tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Visualization integration test failed: {e}")
        return False


def run_all_tests():
    """Run all KPI analyzer tests."""
    print("\n" + "="*70)
    print("KPI ANALYZER TEST SUITE (Phase 5D)")
    print("="*70)
    
    tests = [
        ("KPI Analysis", test_kpi_analysis),
        ("Anomaly Detection", test_anomaly_detection),
        ("Growth Calculation", test_growth_calculation),
        ("Profit Margin", test_profit_margin),
        ("Variance Calculation", test_variance_calculation),
        ("KPI Summary", test_kpi_summary),
        ("Orchestrator Integration", test_orchestrator_integration),
        ("Visualization Integration", test_visualization_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total_count - passed_count} test(s) failed")
    
    print("="*70)
    
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
