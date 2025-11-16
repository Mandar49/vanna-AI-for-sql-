"""
KPI Analyzer Demo (Phase 5D)
Demonstrates quantitative analysis, anomaly detection, and visualization capabilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def demo_kpi_analyzer():
    """Demonstrate KPI analyzer capabilities."""
    print("\n" + "="*70)
    print("KPI ANALYZER DEMO (Phase 5D)")
    print("="*70)
    
    # Import modules
    from kpi_analyzer import (
        analyze_kpis,
        detect_anomalies,
        calculate_growth_rate,
        calculate_profit_margin,
        calculate_variance,
        generate_kpi_summary
    )
    from viz import (
        chart_kpi_dashboard,
        chart_anomalies,
        chart_growth_comparison,
        chart_profit_margin_trend
    )
    from orchestrator import execute_command
    
    # Step 1: Create sample financial data
    print("\n📊 Step 1: Creating sample financial data...")
    
    np.random.seed(42)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Simulate realistic business data with growth trend
    base_revenue = 100000
    revenue = [base_revenue + i * 5000 + np.random.randint(-3000, 8000) for i in range(12)]
    cost = [r * 0.6 + np.random.randint(-2000, 2000) for r in revenue]
    customers = [500 + i * 20 + np.random.randint(-10, 30) for i in range(12)]
    
    df = pd.DataFrame({
        'Month': months,
        'Revenue': revenue,
        'Cost': cost,
        'Customers': customers
    })
    
    print(f"   ✓ Created dataframe with {len(df)} months of data")
    print(f"\n   Sample data:")
    print(df.head(3).to_string(index=False))
    
    # Step 2: Comprehensive KPI Analysis
    print("\n📈 Step 2: Comprehensive KPI analysis...")
    
    result = analyze_kpis(df)
    
    if result['status'] == 'success':
        metrics = result['metrics']
        
        print(f"   ✓ Analysis complete")
        print(f"\n   Summary Statistics:")
        print(f"      Total Revenue: ${metrics['summary']['total']:,.2f}")
        print(f"      Average: ${metrics['summary']['mean']:,.2f}")
        print(f"      Std Dev: ${metrics['summary']['std']:,.2f}")
        print(f"      Range: ${metrics['summary']['min']:,.2f} - ${metrics['summary']['max']:,.2f}")
        
        print(f"\n   Growth Metrics:")
        print(f"      Growth Rate: {metrics['growth']['growth_rate']:.2%}")
        print(f"      Trend: {metrics['growth']['trend']}")
        print(f"      First Value: ${metrics['growth']['first_value']:,.2f}")
        print(f"      Last Value: ${metrics['growth']['last_value']:,.2f}")
        
        print(f"\n   Financial Metrics:")
        print(f"      Profit Margin: {metrics['financial']['profit_margin']:.2%}")
        print(f"      ROI: {metrics['financial']['roi']:.2%}")
        print(f"      Total Profit: ${metrics['financial']['profit']:,.2f}")
        
        print(f"\n   Distribution:")
        print(f"      Coefficient of Variation: {metrics['distribution']['cv']:.2%}")
        print(f"      Skewness: {metrics['distribution']['skewness']:.3f}")
    
    # Step 3: Anomaly Detection
    print("\n🔍 Step 3: Anomaly detection...")
    
    # Add some artificial anomalies
    df_with_anomalies = df.copy()
    df_with_anomalies.loc[5, 'Revenue'] = 180000  # Spike
    df_with_anomalies.loc[8, 'Revenue'] = 85000   # Drop
    
    anomaly_result = detect_anomalies(
        df_with_anomalies,
        value_col='Revenue',
        method='iqr',
        threshold=1.5
    )
    
    if anomaly_result['status'] == 'success':
        print(f"   ✓ Detection complete")
        print(f"      Method: {anomaly_result['method']}")
        print(f"      Anomalies found: {anomaly_result['anomaly_count']}")
        print(f"      Percentage: {anomaly_result['anomaly_percentage']:.1f}%")
        
        if anomaly_result['anomalies']:
            print(f"\n   Detected Anomalies:")
            for i, anomaly in enumerate(anomaly_result['anomalies'][:3], 1):
                month = df_with_anomalies.loc[anomaly['index'], 'Month']
                print(f"      {i}. {month}: ${anomaly['value']:,.2f}")
                print(f"         Expected: {anomaly['expected_range']}")
                print(f"         Deviation: {anomaly['deviation']}")
                print(f"         Severity: {anomaly['severity']:.2f}x")
    
    # Step 4: Specific Metric Calculations
    print("\n💰 Step 4: Specific metric calculations...")
    
    # Growth rate
    current_revenue = df['Revenue'].iloc[-1]
    previous_revenue = df['Revenue'].iloc[0]
    
    growth = calculate_growth_rate(current_revenue, previous_revenue, 'YoY')
    print(f"\n   Year-over-Year Growth:")
    print(f"      Current: ${growth['current']:,.2f}")
    print(f"      Previous: ${growth['previous']:,.2f}")
    print(f"      Growth Rate: {growth['growth_rate']:.2%}")
    print(f"      Status: {growth['status']}")
    
    # Profit margin
    total_revenue = df['Revenue'].sum()
    total_cost = df['Cost'].sum()
    
    margin = calculate_profit_margin(total_revenue, total_cost)
    print(f"\n   Profit Margin:")
    print(f"      Revenue: ${margin['revenue']:,.2f}")
    print(f"      Cost: ${margin['cost']:,.2f}")
    print(f"      Profit: ${margin['profit']:,.2f}")
    print(f"      Margin: {margin['profit_margin']:.2%}")
    print(f"      Status: {margin['status']}")
    
    # Variance from target
    target_revenue = 130000
    actual_revenue = df['Revenue'].mean()
    
    variance = calculate_variance(actual_revenue, target_revenue)
    print(f"\n   Variance Analysis:")
    print(f"      Target: ${variance['target']:,.2f}")
    print(f"      Actual: ${variance['actual']:,.2f}")
    print(f"      Variance: ${variance['variance']:,.2f}")
    print(f"      Variance %: {variance['variance_pct']:.2%}")
    print(f"      Status: {variance['status']}")
    
    # Step 5: Generate KPI Summary
    print("\n📝 Step 5: Generating KPI summary...")
    
    summary = generate_kpi_summary(df)
    print(f"\n{summary}")
    
    # Step 6: Orchestrator Integration
    print("\n🎯 Step 6: Orchestrator integration...")
    
    commands = [
        "analyze KPIs for Sales",
        "analyze financial metrics for Marketing"
    ]
    
    for command in commands:
        print(f"\n   Command: '{command}'")
        result = execute_command(command)
        
        print(f"      Status: {result['status']}")
        print(f"      Message: {result['message']}")
        
        if result['status'] == 'success':
            outputs = result['outputs']
            if 'metrics' in outputs:
                growth_rate = outputs['metrics']['growth'].get('growth_rate', 0)
                print(f"      Growth Rate: {growth_rate:.2%}")
    
    # Step 7: Visualization Generation
    print("\n📊 Step 7: Generating visualizations...")
    
    # Ensure charts directory exists
    Path("./reports/charts").mkdir(parents=True, exist_ok=True)
    
    # KPI Dashboard
    print(f"\n   Creating KPI dashboard...")
    kpis = analyze_kpis(df)
    if kpis['status'] == 'success':
        dashboard_path = chart_kpi_dashboard(kpis['metrics'])
        print(f"      ✓ Dashboard: {dashboard_path}")
    
    # Anomaly Chart
    print(f"\n   Creating anomaly detection chart...")
    anomaly_chart_path = chart_anomalies(
        df_with_anomalies,
        anomaly_result['anomalies'],
        'Revenue'
    )
    print(f"      ✓ Anomalies: {anomaly_chart_path}")
    
    # Growth Comparison
    print(f"\n   Creating growth comparison chart...")
    growth_chart_path = chart_growth_comparison(
        current=current_revenue,
        previous=previous_revenue,
        target=target_revenue,
        labels=['Jan 2024', 'Dec 2024', 'Target']
    )
    print(f"      ✓ Growth: {growth_chart_path}")
    
    # Profit Margin Trend
    print(f"\n   Creating profit margin trend chart...")
    margin_chart_path = chart_profit_margin_trend(
        df,
        revenue_col='Revenue',
        cost_col='Cost',
        date_col='Month'
    )
    print(f"      ✓ Margin Trend: {margin_chart_path}")
    
    # Step 8: Integration Example
    print("\n🔗 Step 8: Complete integration example...")
    
    print(f"\n   Simulating automated KPI report generation...")
    
    # This would typically be scheduled
    def generate_kpi_report(profile):
        """Generate automated KPI report."""
        result = execute_command(f"analyze KPIs for {profile}")
        
        if result['status'] == 'success':
            summary = result['outputs']['summary']
            return summary
        return None
    
    report_summary = generate_kpi_report('Sales')
    if report_summary:
        print(f"      ✓ Automated report generated")
        print(f"\n      Preview:")
        for line in report_summary.split('\n')[:5]:
            print(f"         {line}")
    
    # Summary
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    
    print("\n✅ KPI Analyzer Capabilities Demonstrated:")
    print("   • Comprehensive KPI analysis (summary, growth, financial, distribution)")
    print("   • Anomaly detection (IQR method with severity scoring)")
    print("   • Specific metric calculations (growth, margin, variance)")
    print("   • KPI summary generation (formatted text)")
    print("   • Orchestrator integration (natural language commands)")
    print("   • Visualization generation (4 chart types)")
    print("   • Complete workflow integration")
    
    print("\n💡 Next Steps:")
    print("   • Run: python test_kpi_analyzer.py (comprehensive tests)")
    print("   • Read: KPI_ANALYZER_GUIDE.md (complete documentation)")
    print("   • Try: execute_command('analyze KPIs for <profile>')")
    print("   • View: ./reports/charts/ (generated visualizations)")
    
    print("\n📊 Generated Charts:")
    print(f"   • KPI Dashboard (4-panel overview)")
    print(f"   • Anomaly Detection (with annotations)")
    print(f"   • Growth Comparison (current vs previous vs target)")
    print(f"   • Profit Margin Trend (dual-axis analysis)")
    
    print("="*70)


if __name__ == "__main__":
    try:
        demo_kpi_analyzer()
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("  • Run tests: python test_kpi_analyzer.py")
        print("  • Check guide: KPI_ANALYZER_GUIDE.md")
        print("  • Verify dependencies: pandas, numpy, matplotlib")
