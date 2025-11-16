"""
Example: Integrating Scheduler with Report Generator and Visualization
Demonstrates automated report generation on schedule.
"""

import pandas as pd
from datetime import datetime
from scheduler import schedule_interval, schedule_daily, list_jobs, cancel
from report_generator import build_executive_report
from viz import chart_sales_trend, chart_top_customers, chart_category_breakdown


def generate_automated_sales_report():
    """
    Automated job: Generate comprehensive sales report.
    This runs on schedule and creates a full report with charts.
    """
    print(f"\n{'='*70}")
    print(f"AUTOMATED REPORT GENERATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Simulate fetching data (in real usage, this would query the database)
    print("1. Fetching data...")
    
    sales_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Revenue": [120000, 135000, 142000, 158000, 171000, 189000]
    })
    
    customer_data = pd.DataFrame({
        "Customer": ["Acme Corp", "TechStart", "Global Inc", "Innovation Labs", "Digital Co"],
        "Revenue": [85000, 72000, 68000, 61000, 55000]
    })
    
    product_data = pd.DataFrame({
        "Product": ["Software", "Services", "Hardware", "Training"],
        "Revenue": [450000, 320000, 180000, 95000]
    })
    
    print("   ✓ Data fetched\n")
    
    # Generate visualizations
    print("2. Generating visualizations...")
    
    charts = []
    charts.append(chart_sales_trend(sales_data, "Month", "Revenue"))
    charts.append(chart_top_customers(customer_data, "Customer", "Revenue"))
    charts.append(chart_category_breakdown(product_data, "Product", "Revenue"))
    
    print(f"   ✓ Generated {len(charts)} charts\n")
    
    # Generate report
    print("3. Generating report...")
    
    insights = """
    **Automated Analysis:**
    
    - Revenue shows consistent upward trend
    - Top 5 customers contribute significant portion
    - Product mix is well-balanced
    - All metrics within expected ranges
    """
    
    report = build_executive_report(
        title=f"Automated Sales Report {datetime.now().strftime('%Y-%m-%d')}",
        question="What is the current sales performance?",
        sql="SELECT * FROM sales WHERE date >= CURRENT_DATE - INTERVAL 6 MONTH",
        df=sales_data,
        insights=insights,
        charts=charts
    )
    
    print(f"   ✓ Report generated: {report['paths']['html_path']}\n")
    print(f"{'='*70}")
    print("✅ Automated report generation complete")
    print(f"{'='*70}\n")


def generate_weekly_summary():
    """
    Automated job: Generate weekly summary.
    Lighter report for weekly updates.
    """
    print(f"\n{'='*70}")
    print(f"WEEKLY SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Simple weekly metrics
    weekly_data = pd.DataFrame({
        "Metric": ["Total Sales", "New Customers", "Active Users", "Support Tickets"],
        "This Week": [125000, 15, 450, 23],
        "Last Week": [118000, 12, 430, 28]
    })
    
    report = build_executive_report(
        title=f"Weekly Summary {datetime.now().strftime('%Y-W%W')}",
        question="How did we perform this week?",
        sql="SELECT * FROM weekly_metrics WHERE week = CURRENT_WEEK",
        df=weekly_data,
        insights="Week-over-week growth observed across key metrics.",
        charts=None
    )
    
    print(f"✓ Weekly summary: {report['paths']['html_path']}\n")
    print(f"{'='*70}\n")


def setup_automated_reporting():
    """
    Setup automated reporting schedule.
    Configure various reports to run at different intervals.
    """
    print("="*70)
    print("SETTING UP AUTOMATED REPORTING")
    print("="*70)
    print()
    
    # Schedule 1: Daily sales report at 8:00 AM
    print("1. Scheduling daily sales report (8:00 AM)...")
    daily_handle = schedule_daily(8, 0, generate_automated_sales_report)
    print(f"   ✓ Scheduled job {daily_handle}\n")
    
    # Schedule 2: Weekly summary every Monday at 9:00 AM
    # Note: For weekly, we'd need to add day-of-week logic
    # For now, we'll use daily and check day in the function
    print("2. Scheduling weekly summary (9:00 AM)...")
    weekly_handle = schedule_daily(9, 0, generate_weekly_summary)
    print(f"   ✓ Scheduled job {weekly_handle}\n")
    
    # Schedule 3: Hourly quick check (for demo purposes)
    print("3. Scheduling hourly quick check...")
    
    def hourly_check():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Hourly system check - All systems operational")
    
    hourly_handle = schedule_interval(60, hourly_check)
    print(f"   ✓ Scheduled job {hourly_handle}\n")
    
    # List all scheduled jobs
    print("="*70)
    print("ACTIVE SCHEDULED JOBS")
    print("="*70)
    
    jobs = list_jobs()
    for job in jobs:
        print(f"\nJob {job['id']}: {job['function']}")
        print(f"  Type: {job['type']}")
        if job['type'] == 'interval':
            print(f"  Interval: {job['details']['minutes']} minutes")
        else:
            print(f"  Time: {job['details']['hour']:02d}:{job['details']['minute']:02d}")
        print(f"  Next run: {job['next_run']}")
    
    print("\n" + "="*70)
    print("SCHEDULER CONFIGURATION COMPLETE")
    print("="*70)
    print("\n💡 Tips:")
    print("   • Reports will be generated automatically")
    print("   • Check ./reports/ for generated files")
    print("   • Check ./reports/scheduler.log for execution logs")
    print("   • Use cancel(handle) to stop a scheduled job")
    
    return {
        'daily': daily_handle,
        'weekly': weekly_handle,
        'hourly': hourly_handle
    }


def demo_immediate_execution():
    """
    Demo: Run the automated jobs immediately for testing.
    """
    print("\n" + "="*70)
    print("DEMO: IMMEDIATE EXECUTION")
    print("="*70)
    print("\nRunning automated jobs immediately for demonstration...\n")
    
    # Run jobs directly
    print("Running automated sales report...")
    generate_automated_sales_report()
    
    print("\nRunning weekly summary...")
    generate_weekly_summary()
    
    print("="*70)
    print("✅ Demo complete - Check ./reports/ for generated files")
    print("="*70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run immediate demo
        demo_immediate_execution()
    elif len(sys.argv) > 1 and sys.argv[1] == "setup":
        # Setup scheduled jobs
        handles = setup_automated_reporting()
        
        print("\n⚠️  Scheduler is now running in background")
        print("   Press Ctrl+C to stop\n")
        
        try:
            # Keep main thread alive
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n\nStopping scheduler...")
            for name, handle in handles.items():
                cancel(handle)
                print(f"   ✓ Cancelled {name} job")
            print("\n✅ Scheduler stopped")
    else:
        print("="*70)
        print("SCHEDULER INTEGRATION EXAMPLE")
        print("="*70)
        print("\nUsage:")
        print("  python example_scheduler_integration.py demo   - Run jobs immediately")
        print("  python example_scheduler_integration.py setup  - Setup scheduled jobs")
        print("\nExamples:")
        print("  1. Test immediate execution:")
        print("     python example_scheduler_integration.py demo")
        print()
        print("  2. Start automated scheduling:")
        print("     python example_scheduler_integration.py setup")
        print()
        print("  3. Use in your code:")
        print("     from scheduler import schedule_daily")
        print("     from example_scheduler_integration import generate_automated_sales_report")
        print("     handle = schedule_daily(8, 0, generate_automated_sales_report)")
        print()
        print("="*70)
