"""
Test script for Business Analyst - Data introspection and strategic reasoning
"""
from business_analyst import analyst
import pandas as pd

print("=== Business Analyst Test Suite ===\n")

# Test 1: Simple data analysis
print("Test 1: Top Customers Analysis")
data1 = {
    'CustomerName': ['Mehta Infra LLP', 'Patel Logistics', 'Shetty Steel Co.', 'Deshmukh Textiles', 'Kumar Industries'],
    'TotalSales': [450000, 380000, 320000, 290000, 250000]
}
df1 = pd.DataFrame(data1)
question1 = "Who are our top 5 customers by sales?"

analysis1 = analyst.analyze_results_with_llm(question1, df1)
print(f"Question: {question1}")
print(f"Data Summary: {analysis1['summary']}")
print(f"\nInsight:\n{analysis1['insight']}")
print("\n" + "="*60 + "\n")

# Test 2: Period comparison
print("Test 2: Year-over-Year Sales Comparison")
data2 = {
    'Year': [2023, 2024],
    'TotalSales': [5200000, 5850000]
}
df2 = pd.DataFrame(data2)
question2 = "What were our total sales in 2024 compared to 2023?"

analysis2 = analyst.analyze_results_with_llm(question2, df2)
print(f"Question: {question2}")
print(f"Data Summary: {analysis2['summary']}")
print(f"\nInsight:\n{analysis2['insight']}")

# Check for comparison analysis
comparison = analyst.compare_periods(question2, df2)
if comparison:
    print(f"\nComparison Analysis: {comparison}")
print("\n" + "="*60 + "\n")

# Test 3: Department analysis
print("Test 3: Department Performance")
data3 = {
    'Department': ['Sales', 'Marketing', 'Operations', 'HR'],
    'EmployeeCount': [45, 12, 28, 2],
    'AvgSalary': [125000, 98000, 87000, 121500]
}
df3 = pd.DataFrame(data3)
question3 = "Show me department statistics"

analysis3 = analyst.analyze_results_with_llm(question3, df3)
print(f"Question: {question3}")
print(f"Data Summary: {analysis3['summary']}")
print(f"\nFull Analysis:\n{analysis3['full_analysis']}")

print("\n✅ Business Analyst tests completed!")
