"""
Example: Integrating Report Generator with existing AI BI Agent
Demonstrates how to generate executive reports from query results.
"""

import pandas as pd
from report_generator import build_executive_report


def generate_sample_report():
    """Generate a sample executive report using the report generator."""
    
    # Simulate query results (in real usage, this comes from your SQL execution)
    sample_data = pd.DataFrame({
        "Department": ["Sales", "Marketing", "Engineering", "HR", "Operations"],
        "Headcount": [45, 23, 67, 12, 34],
        "Budget": [450000, 230000, 890000, 120000, 340000],
        "Utilization": ["92%", "87%", "95%", "78%", "88%"]
    })
    
    # Business question
    question = "What is the current resource allocation across departments?"
    
    # SQL query used
    sql_query = """
    SELECT 
        department,
        COUNT(*) as headcount,
        SUM(budget) as budget,
        ROUND(AVG(utilization_rate), 2) as utilization
    FROM employees
    JOIN department_budgets USING (department_id)
    GROUP BY department
    ORDER BY budget DESC
    """
    
    # Analysis insights (in real usage, this comes from business_analyst.py)
    insights = """
    **Key Findings:**
    
    - Engineering has the highest resource allocation with 67 employees and $890K budget
    - Engineering also shows the highest utilization rate at 95%, indicating efficient resource use
    - HR is the smallest department with 12 employees and $120K budget
    - Overall utilization across departments averages 88%, which is healthy
    - Sales department shows strong performance with 92% utilization
    
    **Strategic Implications:**
    
    - Engineering investment is justified by high utilization
    - Consider reviewing HR capacity given lower utilization (78%)
    - Sales and Operations are well-balanced
    """
    
    # Generate the executive report
    result = build_executive_report(
        title="Q4 2024 Resource Allocation Analysis",
        question=question,
        sql=sql_query,
        df=sample_data,
        insights=insights,
        charts=None  # Add chart paths here if visualizations are generated
    )
    
    return result


def integrate_with_existing_workflow():
    """
    Example of how to integrate report generation into existing workflow.
    
    This would be called after:
    1. query_router.py routes the query
    2. SQL is generated and executed
    3. business_analyst.py generates insights
    4. response_composer.py prepares the response
    """
    
    print("="*70)
    print("EXAMPLE: Report Generator Integration")
    print("="*70)
    print()
    
    # Step 1: Generate report
    print("📊 Generating executive report...")
    result = generate_sample_report()
    
    # Step 2: Display results
    print(f"✅ Report generated successfully!\n")
    print(f"Title: {result['title']}")
    print(f"Timestamp: {result['timestamp']}\n")
    
    print("📁 Files created:")
    print(f"   • Markdown: {result['paths']['md_path']}")
    print(f"   • HTML: {result['paths']['html_path']}")
    
    if result['paths']['pdf_path']:
        print(f"   • PDF: {result['paths']['pdf_path']}")
    else:
        print(f"   • PDF: Not generated (optional dependencies not installed)")
    
    print()
    print("💡 Integration Points:")
    print("   1. Call after business_analyst.py generates insights")
    print("   2. Pass SQL query, results DataFrame, and insights")
    print("   3. Optionally include chart paths from visualizations")
    print("   4. Return report paths to user via Flask response")
    print()
    print("="*70)
    print("✅ Report Generator ready for integration")
    print("="*70)


if __name__ == "__main__":
    integrate_with_existing_workflow()
