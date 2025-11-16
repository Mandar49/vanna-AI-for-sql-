"""
Analytics Hub Demo (Phase 5F)
Demonstrates unified executive analytics dashboard capabilities.
"""

def demo_analytics_hub():
    """Demonstrate analytics hub capabilities."""
    print("\n" + "="*70)
    print("ANALYTICS HUB DEMO (Phase 5F)")
    print("="*70)
    
    # Import modules
    from dashboard_gateway import analytics_hub, analytics_api
    from kpi_analyzer import analyze_kpis
    from orchestrator import get_orchestration_history, execute_command
    from profile_manager import list_profiles
    import pandas as pd
    import os
    
    # Step 1: Overview
    print("\n📊 Step 1: Analytics Hub Overview...")
    
    print(f"\n   The Analytics Hub is a unified executive dashboard that consolidates:")
    print(f"      • Latest KPIs (from kpi_analyzer)")
    print(f"      • Recent charts (from viz module)")
    print(f"      • Voice summaries (profile activity)")
    print(f"      • Orchestration history (command log)")
    print(f"      • System statistics (overall health)")
    
    # Step 2: KPI Integration
    print("\n📈 Step 2: KPI Integration...")
    
    # Create sample data
    df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [100000, 120000, 115000, 135000, 142000, 138000],
        'Cost': [60000, 70000, 65000, 75000, 80000, 78000]
    })
    
    result = analyze_kpis(df)
    
    if result['status'] == 'success':
        metrics = result['metrics']
        
        print(f"\n   KPIs Calculated:")
        print(f"      Total Revenue: ${metrics['summary']['total']:,.2f}")
        print(f"      Average Revenue: ${metrics['summary']['mean']:,.2f}")
        print(f"      Growth Rate: {metrics['growth'].get('growth_rate', 0):.2%}")
        print(f"      Profit Margin: {metrics['financial'].get('profit_margin', 0):.2%}")
        print(f"      ROI: {metrics['financial'].get('roi', 0):.2%}")
    
    # Step 3: Charts Integration
    print("\n📉 Step 3: Charts Integration...")
    
    charts_dir = "./reports/charts"
    
    if os.path.exists(charts_dir):
        charts = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
        
        print(f"\n   Charts Available: {len(charts)}")
        
        if charts:
            print(f"      Recent charts:")
            for chart in charts[:5]:
                print(f"         • {chart}")
    else:
        print(f"\n   Charts directory will be created on first chart generation")
    
    # Step 4: Voice Summaries
    print("\n🎙 Step 4: Voice Summaries Integration...")
    
    profiles = list_profiles()
    
    print(f"\n   Profiles: {len(profiles)}")
    
    for profile in profiles[:5]:
        summary = f"Profile {profile['name']} has {profile['interaction_count']} interactions"
        print(f"      • {summary}")
    
    # Step 5: Orchestration History
    print("\n🎯 Step 5: Orchestration History...")
    
    # Execute some commands to create history
    print(f"\n   Executing sample commands...")
    
    commands = [
        "list profiles",
        "analyze KPIs for Sales"
    ]
    
    for command in commands:
        result = execute_command(command)
        print(f"      • '{command}' → {result['status']}")
    
    # Get history
    history = get_orchestration_history(limit=5)
    
    print(f"\n   Command History: {len(history)} entries")
    
    for item in history[:3]:
        print(f"      • {item['command']}")
        print(f"        Status: {item['result']['status']}")
        print(f"        Message: {item['result']['message']}")
    
    # Step 6: System Statistics
    print("\n📊 Step 6: System Statistics...")
    
    from dashboard_gateway import get_recent_reports
    
    reports = get_recent_reports()
    
    charts_count = 0
    if os.path.exists(charts_dir):
        charts_count = len([f for f in os.listdir(charts_dir) if f.endswith('.png')])
    
    print(f"\n   System Overview:")
    print(f"      Total Profiles: {len(profiles)}")
    print(f"      Total Reports: {len(reports)}")
    print(f"      Total Charts: {charts_count}")
    print(f"      Commands Executed: {len(history)}")
    
    # Step 7: Dashboard Sections
    print("\n🎨 Step 7: Dashboard Sections...")
    
    print(f"\n   The Analytics Hub includes:")
    
    sections = [
        {
            'name': 'Header',
            'description': 'Title, subtitle, and last updated timestamp'
        },
        {
            'name': 'KPI Cards (2x2 Grid)',
            'description': 'Total Revenue, Average, Profit Margin, Growth Rate'
        },
        {
            'name': 'Recent Charts',
            'description': 'Latest 5 charts with click-to-view functionality'
        },
        {
            'name': 'Voice Summaries',
            'description': 'Latest 5 profile activity summaries'
        },
        {
            'name': 'Recent Commands',
            'description': 'Latest 5 orchestration commands with status'
        },
        {
            'name': 'System Overview',
            'description': 'Full-width section with system statistics'
        },
        {
            'name': 'Refresh Button',
            'description': 'Floating action button to reload dashboard'
        }
    ]
    
    for i, section in enumerate(sections, 1):
        print(f"\n      {i}. {section['name']}")
        print(f"         {section['description']}")
    
    # Step 8: API Access
    print("\n🔌 Step 8: API Access...")
    
    print(f"\n   Analytics Hub provides two endpoints:")
    print(f"      1. Web UI: /dashboard/analytics")
    print(f"         • Full HTML dashboard")
    print(f"         • Interactive elements")
    print(f"         • Responsive design")
    
    print(f"\n      2. JSON API: /dashboard/analytics/api")
    print(f"         • Programmatic access")
    print(f"         • Returns all analytics data")
    print(f"         • Easy integration")
    
    print(f"\n   Example API Response:")
    print(f"      {{")
    print(f"        'success': true,")
    print(f"        'data': {{")
    print(f"          'kpis': {{ ... }},")
    print(f"          'charts_count': {charts_count},")
    print(f"          'history_count': {len(history)},")
    print(f"          'profiles_count': {len(profiles)}")
    print(f"        }}")
    print(f"      }}")
    
    # Step 9: Integration Examples
    print("\n🔗 Step 9: Integration Examples...")
    
    examples = [
        {
            'name': 'Access Analytics Hub',
            'code': """
from flask import Flask
from dashboard_gateway import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)
app.run(debug=True)

# Visit: http://localhost:5000/dashboard/analytics
            """
        },
        {
            'name': 'Fetch Analytics via API',
            'code': """
import requests

response = requests.get('http://localhost:5000/dashboard/analytics/api')
data = response.json()

if data['success']:
    print(f"Profiles: {data['data']['profiles_count']}")
    print(f"Charts: {data['data']['charts_count']}")
            """
        },
        {
            'name': 'Automated Daily Report',
            'code': """
def daily_analytics_report():
    response = requests.get('http://localhost:5000/dashboard/analytics/api')
    data = response.json()
    # Generate report...

from scheduler import schedule_daily
schedule_daily(9, 0, daily_analytics_report)
            """
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n      Example {i}: {example['name']}")
        print(f"      {example['code'].strip()[:100]}...")
    
    # Step 10: Features
    print("\n✨ Step 10: Key Features...")
    
    features = [
        "Unified Dashboard - All metrics in one place",
        "Real-Time Data - Latest KPIs and statistics",
        "Interactive Elements - Clickable charts and refresh",
        "Professional Design - Modern gradient and card layout",
        "API Access - Programmatic data retrieval",
        "Responsive Design - Works on all devices",
        "Status Indicators - Color-coded success/error badges",
        "System Health - Overall system statistics"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"      {i}. {feature}")
    
    # Summary
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    
    print("\n✅ Analytics Hub Capabilities Demonstrated:")
    print("   • KPI integration (Phase 5D)")
    print("   • Charts integration (Phase 2)")
    print("   • Voice summaries (profile activity)")
    print("   • Orchestration history (Phase 4B)")
    print("   • System statistics (overall health)")
    print("   • Unified dashboard view")
    print("   • API access (JSON endpoint)")
    
    print("\n💡 Next Steps:")
    print("   • Start Flask app: python -m flask run")
    print("   • Visit: http://localhost:5000/dashboard/analytics")
    print("   • API: http://localhost:5000/dashboard/analytics/api")
    print("   • Run tests: python test_dashboard_analytics.py")
    print("   • Read guide: ANALYTICS_HUB_GUIDE.md")
    
    print("\n📊 Dashboard Sections:")
    print("   ✓ Header (title, subtitle, timestamp)")
    print("   ✓ KPI Cards (revenue, growth, margin)")
    print("   ✓ Recent Charts (latest 5 visualizations)")
    print("   ✓ Voice Summaries (profile activity)")
    print("   ✓ Recent Commands (orchestration history)")
    print("   ✓ System Overview (profiles, reports, charts)")
    print("   ✓ Refresh Button (reload dashboard)")
    
    print("\n🎯 Integration:")
    print("   Analytics Hub integrates with ALL subsystems:")
    print("   ✓ KPI Analyzer (Phase 5D)")
    print("   ✓ Visualization Engine (Phase 2)")
    print("   ✓ Profile Manager (Phase 3A)")
    print("   ✓ Orchestrator (Phase 4B)")
    print("   ✓ Report Generator (Phase 1)")
    print("   ✓ Dashboard Gateway (Phase 4A)")
    
    print("="*70)


if __name__ == "__main__":
    try:
        demo_analytics_hub()
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("  • Run tests: python test_dashboard_analytics.py")
        print("  • Check guide: ANALYTICS_HUB_GUIDE.md")
        print("  • Verify subsystems: python orchestrator.py")
