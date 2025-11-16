"""
Test script for the Dual-Brain Intelligence System
"""
from query_router import router

# Test cases
test_queries = [
    ("What is the phone number of Priya Sharma?", "sql"),
    ("Tell me about Lenovo company.", "general"),
    ("Who won the last cricket world cup?", "general"),
    ("List all customers in Mumbai.", "sql"),
    ("What is HTML?", "general"),
    ("Show me all employees in HR department", "sql"),
    ("Explain artificial intelligence", "general"),
    ("What is the average salary?", "sql"),
]

print("=== Testing Query Classification ===\n")

for query, expected_type in test_queries:
    classified_type = router.classify_query(query)
    status = "✓" if classified_type == expected_type else "✗"
    print(f"{status} Query: '{query}'")
    print(f"  Expected: {expected_type} | Got: {classified_type}\n")

print("\n=== Testing General Brain Response ===\n")

# Test a general query
general_query = "What is Lenovo?"
result = router._handle_general_query(general_query, [])
print(f"Query: {general_query}")
print(f"Response: {result['answer'][:200]}...")
print(f"Type: {result['type']}")

print("\n✅ Dual-brain system test completed!")
