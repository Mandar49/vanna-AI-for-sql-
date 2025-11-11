"""
Test script for Cognitive Fusion Layer
Tests context memory, persona selection, and integrated reasoning
"""
from context_memory import memory
from response_composer import composer
from business_analyst import analyst
import pandas as pd

print("=== Cognitive Fusion Layer Test Suite ===\n")

# Test 1: Context Memory
print("Test 1: Context Memory")
memory.clear_memory()
memory.remember("What are our top customers?", "Top customers are Mehta Infra and Patel Logistics", 
                "SELECT * FROM customers", "Strong customer base", "analyst")
memory.remember("What about sales trends?", "Sales increasing by 12%", 
                "SELECT * FROM sales", "Positive growth", "strategist")

print(f"Memory entries: {len(memory.history)}")
print(f"Last query: {memory.get_last_query()['query']}")
print(f"\nContext recall:\n{memory.recall_context(last_n=2)}")
print("\n" + "="*60 + "\n")

# Test 2: Persona Detection
print("Test 2: Persona Detection")
test_queries = [
    ("Who are the top 5 customers?", "analyst"),
    ("What strategy should we use for growth?", "strategist"),
    ("Write a thank you email to John", "writer"),
    ("Show me sales data", "analyst"),
    ("What are the future trends?", "strategist"),
]

for query, expected in test_queries:
    detected = composer.detect_persona(query)
    status = "OK" if detected == expected else "MISMATCH"
    print(f"[{status}] '{query}' -> {detected} (expected: {expected})")

print("\n" + "="*60 + "\n")

# Test 3: Trend Analysis
print("Test 3: Trend Analysis")
data = {
    'Year': [2022, 2023, 2024],
    'Sales': [1000000, 1100000, 1250000]
}
df = pd.DataFrame(data)
trend = analyst.analyze_trends(df)
print(f"Data:\n{df}")
print(f"\nTrend Analysis: {trend}")
print("\n" + "="*60 + "\n")

# Test 4: Memory Statistics
print("Test 4: Memory Statistics")
stats = memory.get_statistics()
print(f"Total exchanges: {stats['total_exchanges']}")
print(f"Max capacity: {stats['max_capacity']}")
print(f"Memory file: {stats['memory_file']}")
print("\n" + "="*60 + "\n")

# Test 5: Related Context
print("Test 5: Related Context Retrieval")
memory.remember("Show me customer data", "Here are the customers", None, None, "analyst")
memory.remember("What are product sales?", "Product sales data", None, None, "analyst")
memory.remember("Customer satisfaction scores", "Satisfaction is high", None, None, "analyst")

related = memory.get_related_context("Tell me about customers")
print(f"Query: 'Tell me about customers'")
print(f"Related exchanges found: {len(related)}")
for entry in related:
    print(f"  - {entry['query']}")

print("\n=== All Cognitive Fusion tests completed! ===")
