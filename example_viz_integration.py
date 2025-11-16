"""
Example: Integrating Visualization Engine with Report Generator
Demonstrates end-to-end report generation with charts.
"""

import pandas as pd
from viz import chart_sales_trend, chart_top_customers, chart_category_breakdown
from report_generator import build_executive_report


def generate_complete_report_with_charts():
    """
    Generate a complete executive report with visualizations.
    Demonstrates full integration of Phase 1 + Phase 2.
    """
    
    print("="*70)
    print("EXAMPLE: Complete Report with Visualizations")
    print("="*70)
    print()
    
    # Step 1: Prepare sample data (in real usage, from SQL query)
    print("📊 Step 1: Preparing data...")
    
    # Sales trend data
    trend_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Revenue": [120000, 135000, 142000, 158000, 171000, 189000],
        "Orders": [450, 480, 510, 550, 590, 630]
    })
    
    # Top customers data
    customers_data = pd.DataFrame({
        "Customer": [
            "Global Tech Corp", "Innovation Partners", "Digital Solutions",
            "Future Systems", "Smart Industries", "Prime Enterprises",
            "Elite Partners", "Mega Corp", "Quantum Labs", "Nano Tech"
        ],
        "Revenue": [85000, 72000, 68000, 61000, 55000, 49000, 43000, 38000, 32000, 28000]
    })
    
    # Category breakdown data
    category_data = pd.DataFrame({
        "Product_Line": ["Enterprise Software", "Cloud Services", "Consulting", "Support", "Training"],
        "Revenue": [450000, 320000, 180000, 95000, 55000]
    })
    
    print("   ✓ Data prepared\n")
    
    # Step 2: Generate charts
    print("📈 Step 2: Generating visualizations...")
    
    chart_paths = []
    
    # Chart 1: Revenue trend
    trend_chart = chart_sales_trend(trend_data, "Month", "Revenue")
    chart_paths.append(trend_chart)
    print(f"   ✓ Revenue trend chart: {trend_chart}")
    
    # Chart 2: Top customers
    customers_chart = chart_top_customers(customers_data, "Customer", "Revenue", top_n=8)
    chart_paths.append(customers_chart)
    print(f"   ✓ Top customers chart: {customers_chart}")
    
    # Chart 3: Product line breakdown
    category_chart = chart_category_breakdown(category_data, "Product_Line", "Revenue")
    chart_paths.append(category_chart)
    print(f"   ✓ Product breakdown chart: {category_chart}\n")
    
    # Step 3: Prepare analysis insights
    print("🧠 Step 3: Preparing insights...")
    
    insights = """
    **Executive Summary:**
    
    Our H1 2024 performance analysis reveals strong growth momentum across all key metrics:
    
    **Revenue Growth:**
    - Total revenue increased 57.5% from January ($120K) to June ($189K)
    - Consistent month-over-month growth averaging 9.5%
    - Q2 performance exceeded Q1 by 28%
    
    **Customer Performance:**
    - Top 10 customers contribute $531K in revenue
    - Global Tech Corp leads with $85K, representing 16% of top customer revenue
    - Strong diversification with no single customer exceeding 20% concentration
    
    **Product Mix:**
    - Enterprise Software dominates at 40.5% of total revenue ($450K)
    - Cloud Services shows strong adoption at 28.8% ($320K)
    - Professional services (Consulting, Support, Training) represent 29.7%
    
    **Strategic Implications:**
    - Growth trajectory suggests $2.3M annual run rate if sustained
    - Customer diversification reduces concentration risk
    - Product portfolio is well-balanced between software and services
    """
    
    print("   ✓ Insights prepared\n")
    
    # Step 4: Generate complete report
    print("📄 Step 4: Generating executive report...")
    
    # Combine all data for the report
    combined_data = pd.DataFrame({
        "Metric": ["Total Revenue", "Total Customers", "Avg Order Value", "Growth Rate"],
        "Value": ["$1,115,000", "10", "$1,770", "57.5%"]
    })
    
    sql_query = """
    -- Revenue Trend Analysis
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') as month,
        SUM(revenue) as revenue,
        COUNT(DISTINCT order_id) as orders
    FROM sales
    WHERE order_date >= '2024-01-01' AND order_date < '2024-07-01'
    GROUP BY month
    ORDER BY month;
    
    -- Top Customers
    SELECT 
        customer_name,
        SUM(revenue) as revenue
    FROM sales
    GROUP BY customer_name
    ORDER BY revenue DESC
    LIMIT 10;
    
    -- Product Line Breakdown
    SELECT 
        product_line,
        SUM(revenue) as revenue
    FROM sales
    GROUP BY product_line
    ORDER BY revenue DESC;
    """
    
    result = build_executive_report(
        title="H1 2024 Business Performance Review",
        question="How did our business perform in the first half of 2024 across revenue, customers, and product lines?",
        sql=sql_query,
        df=combined_data,
        insights=insights,
        charts=chart_paths  # Pass the chart paths here!
    )
    
    print(f"   ✓ Report generated\n")
    
    # Step 5: Display results
    print("="*70)
    print("RESULTS")
    print("="*70)
    print(f"\n📊 Report: {result['title']}")
    print(f"🕐 Generated: {result['timestamp']}")
    print(f"\n📁 Files created:")
    print(f"   • Markdown: {result['paths']['md_path']}")
    print(f"   • HTML: {result['paths']['html_path']}")
    if result['paths']['pdf_path']:
        print(f"   • PDF: {result['paths']['pdf_path']}")
    
    print(f"\n📈 Charts embedded: {len(chart_paths)}")
    for i, chart in enumerate(chart_paths, 1):
        print(f"   {i}. {chart}")
    
    print("\n" + "="*70)
    print("✅ Complete report with visualizations ready!")
    print("="*70)
    print("\n💡 Next Steps:")
    print("   1. Open the HTML file in a browser to view the report")
    print("   2. Charts are embedded as image links")
    print("   3. Share the reports folder with stakeholders")
    print("   4. Integrate into your Flask app for automated delivery")
    
    return result


def quick_chart_demo():
    """Quick demonstration of individual chart types."""
    print("\n" + "="*70)
    print("QUICK CHART DEMO")
    print("="*70 + "\n")
    
    # Demo 1: Line chart
    print("1. Line Chart (Sales Trend)")
    df1 = pd.DataFrame({
        "Week": [f"Week {i}" for i in range(1, 9)],
        "Sales": [15000, 17000, 16500, 19000, 21000, 23000, 22500, 25000]
    })
    path1 = chart_sales_trend(df1, "Week", "Sales")
    print(f"   ✓ {path1}\n")
    
    # Demo 2: Bar chart
    print("2. Horizontal Bar Chart (Top Products)")
    df2 = pd.DataFrame({
        "Product": ["Product A", "Product B", "Product C", "Product D", "Product E"],
        "Units_Sold": [1200, 980, 850, 720, 650]
    })
    path2 = chart_top_customers(df2, "Product", "Units_Sold", top_n=5)
    print(f"   ✓ {path2}\n")
    
    # Demo 3: Pie chart
    print("3. Pie Chart (Market Share)")
    df3 = pd.DataFrame({
        "Region": ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"],
        "Market_Share": [35, 28, 22, 10, 5]
    })
    path3 = chart_category_breakdown(df3, "Region", "Market_Share")
    print(f"   ✓ {path3}\n")
    
    print("="*70)
    print("✅ All chart types demonstrated")
    print("="*70)


if __name__ == "__main__":
    # Run complete integration example
    generate_complete_report_with_charts()
    
    # Run quick demo
    quick_chart_demo()
