"""
Test Metric Calculation Engine
Validates percentage precision with ≤0.1% tolerance
"""
from business_analyst import analyst
import pandas as pd

def test_growth_metric():
    """Test 1: Growth percentage calculation"""
    print("\n" + "="*70)
    print("TEST 1: Growth Metric Calculation")
    print("="*70)
    
    # Test data
    df = pd.DataFrame({
        'Year': [2023, 2024],
        'Sales': [1000, 1100]
    })
    
    print("\n[DATA]")
    print(df.to_string(index=False))
    
    # Calculate growth
    result = analyst.calculate_metric(df, 'growth')
    
    if 'ComputedMetric' in result.columns:
        growth = result['ComputedMetric'].iloc[0]
        expected_growth = ((1100 - 1000) / 1000) * 100  # 10%
        
        print(f"\n[RESULT]")
        print(f"   Calculated growth: {growth}%")
        print(f"   Expected growth: {expected_growth}%")
        print(f"   Difference: {abs(growth - expected_growth)}%")
        
        if abs(growth - expected_growth) <= 0.1:
            print("\n[PASS] Growth calculation within 0.1% tolerance")
            return True
        else:
            print(f"\n[FAIL] Growth calculation outside tolerance")
            return False
    else:
        print("\n[FAIL] ComputedMetric column not added")
        return False

def test_ratio_metric():
    """Test 2: Ratio calculation"""
    print("\n" + "="*70)
    print("TEST 2: Ratio Metric Calculation")
    print("="*70)
    
    # Test data
    df = pd.DataFrame({
        'Revenue': [1000, 2000, 3000],
        'Cost': [600, 1200, 1800]
    })
    
    print("\n[DATA]")
    print(df.to_string(index=False))
    
    # Calculate ratio
    result = analyst.calculate_metric(df, 'ratio')
    
    if 'ComputedMetric' in result.columns:
        ratios = result['ComputedMetric'].tolist()
        expected_ratios = [1000/600, 2000/1200, 3000/1800]
        
        print(f"\n[RESULT]")
        print(f"   Calculated ratios: {[f'{r:.4f}' for r in ratios]}")
        print(f"   Expected ratios: {[f'{r:.4f}' for r in expected_ratios]}")
        
        # Check accuracy
        all_accurate = all(abs(ratios[i] - expected_ratios[i]) <= 0.001 for i in range(len(ratios)))
        
        if all_accurate:
            print("\n[PASS] Ratio calculation accurate")
            return True
        else:
            print("\n[FAIL] Ratio calculation inaccurate")
            return False
    else:
        print("\n[FAIL] ComputedMetric column not added")
        return False

def test_share_metric():
    """Test 3: Share percentage calculation"""
    print("\n" + "="*70)
    print("TEST 3: Share Metric Calculation")
    print("="*70)
    
    # Test data
    df = pd.DataFrame({
        'Product': ['A', 'B', 'C'],
        'Sales': [100, 200, 300]
    })
    
    print("\n[DATA]")
    print(df.to_string(index=False))
    
    # Calculate share
    result = analyst.calculate_metric(df, 'share')
    
    if 'ComputedMetric' in result.columns:
        shares = result['ComputedMetric'].tolist()
        total = 100 + 200 + 300
        expected_shares = [(100/total)*100, (200/total)*100, (300/total)*100]
        
        print(f"\n[RESULT]")
        print(f"   Calculated shares: {[f'{s:.2f}%' for s in shares]}")
        print(f"   Expected shares: {[f'{s:.2f}%' for s in expected_shares]}")
        
        # Check if all shares are within 0.1% tolerance
        all_within_tolerance = all(abs(shares[i] - expected_shares[i]) <= 0.1 for i in range(len(shares)))
        
        # Also check if shares sum to 100%
        total_share = sum(shares)
        print(f"   Total share: {total_share:.2f}%")
        
        if all_within_tolerance and abs(total_share - 100) <= 0.1:
            print("\n[PASS] Share calculation within 0.1% tolerance")
            return True
        else:
            print("\n[FAIL] Share calculation outside tolerance")
            return False
    else:
        print("\n[FAIL] ComputedMetric column not added")
        return False

def test_aov_metric():
    """Test 4: Average Order Value calculation"""
    print("\n" + "="*70)
    print("TEST 4: AOV Metric Calculation")
    print("="*70)
    
    # Test data
    df = pd.DataFrame({
        'TotalAmount': [1000, 2000, 3000],
        'OrderCount': [10, 20, 30]
    })
    
    print("\n[DATA]")
    print(df.to_string(index=False))
    
    # Calculate AOV
    result = analyst.calculate_metric(df, 'aov')
    
    if 'ComputedMetric' in result.columns:
        aovs = result['ComputedMetric'].tolist()
        expected_aovs = [1000/10, 2000/20, 3000/30]
        
        print(f"\n[RESULT]")
        print(f"   Calculated AOVs: {[f'{a:.2f}' for a in aovs]}")
        print(f"   Expected AOVs: {[f'{a:.2f}' for a in expected_aovs]}")
        
        # Check accuracy
        all_accurate = all(abs(aovs[i] - expected_aovs[i]) <= 0.01 for i in range(len(aovs)))
        
        if all_accurate:
            print("\n[PASS] AOV calculation accurate")
            return True
        else:
            print("\n[FAIL] AOV calculation inaccurate")
            return False
    else:
        print("\n[FAIL] ComputedMetric column not added")
        return False

def test_metric_detection():
    """Test 5: Metric detection from queries"""
    print("\n" + "="*70)
    print("TEST 5: Metric Detection")
    print("="*70)
    
    test_queries = [
        ("What is the growth from 2023 to 2024?", ['growth']),
        ("Calculate the ratio of revenue to cost", ['ratio']),
        ("What percentage share does each product have?", ['share']),
        ("What is the average order value?", ['aov']),
        ("Compare sales between years", ['compare']),
        ("Show me the increase in revenue", ['growth']),
        ("What proportion of sales comes from product A?", ['ratio', 'share']),
    ]
    
    all_passed = True
    
    for query, expected_metrics in test_queries:
        detected = analyst.detect_metrics(query)
        
        print(f"\n[TEST] Query: '{query}'")
        print(f"   Detected: {detected}")
        print(f"   Expected: {expected_metrics}")
        
        # Check if at least one expected metric was detected
        if any(m in detected for m in expected_metrics):
            print("   [OK] Metric detected correctly")
        else:
            print(f"   [FAIL] Expected one of {expected_metrics}, got {detected}")
            all_passed = False
    
    if all_passed:
        print("\n[PASS] Metric detection working correctly")
        return True
    else:
        print("\n[FAIL] Some metric detections failed")
        return False

def test_apply_metrics():
    """Test 6: Apply metrics to DataFrame"""
    print("\n" + "="*70)
    print("TEST 6: Apply Metrics Integration")
    print("="*70)
    
    # Test data
    df = pd.DataFrame({
        'Year': [2023, 2024],
        'Sales': [1000, 1200]
    })
    
    query = "What is the growth in sales from 2023 to 2024?"
    
    print(f"\n[QUERY] {query}")
    print("\n[DATA]")
    print(df.to_string(index=False))
    
    # Apply metrics
    result = analyst.apply_metrics(df, query)
    
    if 'ComputedMetric' in result.columns:
        print(f"\n[RESULT]")
        print(result.to_string(index=False))
        
        growth = result['ComputedMetric'].iloc[0]
        expected_growth = ((1200 - 1000) / 1000) * 100  # 20%
        
        print(f"\n[VALIDATION]")
        print(f"   Calculated growth: {growth}%")
        print(f"   Expected growth: {expected_growth}%")
        
        if abs(growth - expected_growth) <= 0.1:
            print("\n[PASS] Apply metrics working correctly")
            return True
        else:
            print("\n[FAIL] Metric calculation incorrect")
            return False
    else:
        print("\n[FAIL] Metrics not applied")
        return False

def test_precision_tolerance():
    """Test 7: Precision tolerance validation"""
    print("\n" + "="*70)
    print("TEST 7: Precision Tolerance (<=0.1%)")
    print("="*70)
    
    # Test with various precision scenarios
    test_cases = [
        (100, 110, 10.0),      # Exact 10%
        (100, 110.05, 10.05),  # 10.05%
        (1000, 1001, 0.1),     # 0.1%
        (12345, 12468, 0.996), # ~1%
    ]
    
    all_passed = True
    
    for v1, v2, expected_growth in test_cases:
        df = pd.DataFrame({
            'Period': ['Start', 'End'],
            'Value': [v1, v2]
        })
        
        result = analyst.calculate_metric(df, 'growth')
        
        if 'ComputedMetric' in result.columns:
            calculated_growth = result['ComputedMetric'].iloc[0]
            difference = abs(calculated_growth - expected_growth)
            
            print(f"\n[TEST] {v1} -> {v2}")
            print(f"   Calculated: {calculated_growth:.4f}%")
            print(f"   Expected: {expected_growth:.4f}%")
            print(f"   Difference: {difference:.4f}%")
            
            if difference <= 0.1:
                print("   [OK] Within 0.1% tolerance")
            else:
                print("   [FAIL] Outside 0.1% tolerance")
                all_passed = False
        else:
            print(f"\n[FAIL] Metric not calculated for {v1} -> {v2}")
            all_passed = False
    
    if all_passed:
        print("\n[PASS] All precision tests within 0.1% tolerance")
        return True
    else:
        print("\n[FAIL] Some precision tests failed")
        return False

def run_all_tests():
    """Run all metric engine tests"""
    print("\n" + "="*70)
    print("METRIC CALCULATION ENGINE TEST SUITE")
    print("="*70)
    print("[INFO] Testing modular ratio engine")
    print("[INFO] Validating percentage precision <=0.1% tolerance")
    
    results = []
    
    try:
        results.append(("Growth Metric", test_growth_metric()))
        results.append(("Ratio Metric", test_ratio_metric()))
        results.append(("Share Metric", test_share_metric()))
        results.append(("AOV Metric", test_aov_metric()))
        results.append(("Metric Detection", test_metric_detection()))
        results.append(("Apply Metrics", test_apply_metrics()))
        results.append(("Precision Tolerance", test_precision_tolerance()))
        
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
            print("\n[SUCCESS] All metric engine tests passed!")
            print("[INFO] Modular ratio engine implemented")
            print("[INFO] Percentage precision <=0.1% tolerance validated")
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
