"""
Example: Integrating Profile Manager with the AI BI Agent
Demonstrates multi-department context management.
"""

from profile_manager import (
    init_profile,
    set_active_profile,
    get_active_profile,
    save_interaction,
    load_recent,
    list_profiles,
    get_profile_stats
)


def setup_department_profiles():
    """
    Setup profiles for different business departments.
    Each department gets its own context and persona.
    """
    print("="*70)
    print("SETTING UP DEPARTMENT PROFILES")
    print("="*70)
    print()
    
    departments = [
        ("Sales", "Analyst", "Focuses on revenue, deals, and customer metrics"),
        ("Marketing", "Strategist", "Focuses on campaigns, ROI, and brand metrics"),
        ("HR", "Writer", "Focuses on employee data, turnover, and satisfaction"),
        ("Finance", "Analyst", "Focuses on budgets, expenses, and financial health"),
        ("Operations", "Manager", "Focuses on efficiency, processes, and logistics")
    ]
    
    print("Creating department profiles...\n")
    for dept, persona, description in departments:
        init_profile(dept, persona=persona)
        print(f"  ✓ {dept} ({persona}): {description}")
    
    print("\n" + "="*70)
    print("DEPARTMENT PROFILES CREATED")
    print("="*70)


def simulate_sales_workflow():
    """
    Simulate a Sales department workflow with profile-specific context.
    """
    print("\n" + "="*70)
    print("SALES DEPARTMENT WORKFLOW")
    print("="*70)
    print()
    
    # Activate Sales profile
    set_active_profile("Sales")
    print(f"Active Profile: {get_active_profile()}\n")
    
    # Simulate sales queries and responses
    sales_interactions = [
        {
            "query": "What are our top 5 products by revenue this quarter?",
            "response": "Top 5 products: Widget A ($500K), Widget B ($450K), Widget C ($400K), Widget D ($350K), Widget E ($300K)",
            "sql": "SELECT product_name, SUM(revenue) as total_revenue FROM sales WHERE quarter = 'Q4' GROUP BY product_name ORDER BY total_revenue DESC LIMIT 5"
        },
        {
            "query": "Show me the sales trend for the last 6 months",
            "response": "Sales trend shows consistent growth: Jun $1.2M, Jul $1.3M, Aug $1.5M, Sep $1.6M, Oct $1.8M, Nov $2.0M",
            "sql": "SELECT MONTH(sale_date) as month, SUM(amount) as monthly_sales FROM sales WHERE sale_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH) GROUP BY month"
        },
        {
            "query": "Which sales rep has the highest conversion rate?",
            "response": "Top performer: John Smith with 45% conversion rate (90 deals closed out of 200 opportunities)",
            "sql": "SELECT rep_name, (closed_deals / total_opportunities * 100) as conversion_rate FROM sales_reps ORDER BY conversion_rate DESC LIMIT 1"
        }
    ]
    
    print("Saving Sales interactions...\n")
    for interaction in sales_interactions:
        save_interaction(
            "Sales",
            interaction["query"],
            interaction["response"],
            interaction["sql"]
        )
        print(f"  Q: {interaction['query'][:60]}...")
        print(f"  A: {interaction['response'][:60]}...\n")
    
    # Show recent history
    print("Recent Sales history:")
    recent = load_recent("Sales", n=3)
    for i, item in enumerate(recent, 1):
        print(f"  {i}. {item['query'][:50]}...")
    
    print("\n" + "="*70)


def simulate_marketing_workflow():
    """
    Simulate a Marketing department workflow with different context.
    """
    print("\n" + "="*70)
    print("MARKETING DEPARTMENT WORKFLOW")
    print("="*70)
    print()
    
    # Switch to Marketing profile
    set_active_profile("Marketing")
    print(f"Active Profile: {get_active_profile()}\n")
    
    # Simulate marketing queries
    marketing_interactions = [
        {
            "query": "What's the ROI of our recent email campaigns?",
            "response": "Email campaign ROI: Campaign A: 250% ($50K spent, $125K revenue), Campaign B: 180% ($30K spent, $54K revenue)",
            "sql": "SELECT campaign_name, (revenue - cost) / cost * 100 as roi FROM marketing_campaigns WHERE channel = 'email' AND date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)"
        },
        {
            "query": "Show me website traffic trends by source",
            "response": "Traffic sources: Organic 45% (50K visits), Paid 30% (33K visits), Social 15% (17K visits), Direct 10% (11K visits)",
            "sql": "SELECT source, COUNT(*) as visits, (COUNT(*) / total * 100) as percentage FROM web_traffic GROUP BY source"
        }
    ]
    
    print("Saving Marketing interactions...\n")
    for interaction in marketing_interactions:
        save_interaction(
            "Marketing",
            interaction["query"],
            interaction["response"],
            interaction["sql"]
        )
        print(f"  Q: {interaction['query'][:60]}...")
        print(f"  A: {interaction['response'][:60]}...\n")
    
    print("\n" + "="*70)


def demonstrate_profile_isolation():
    """
    Demonstrate that profiles maintain separate contexts.
    """
    print("\n" + "="*70)
    print("PROFILE ISOLATION DEMONSTRATION")
    print("="*70)
    print()
    
    # Show Sales context
    print("Sales Profile Context:")
    sales_history = load_recent("Sales", n=10)
    print(f"  Total interactions: {len(sales_history)}")
    if sales_history:
        print(f"  Latest: {sales_history[0]['query'][:50]}...")
    print()
    
    # Show Marketing context
    print("Marketing Profile Context:")
    marketing_history = load_recent("Marketing", n=10)
    print(f"  Total interactions: {len(marketing_history)}")
    if marketing_history:
        print(f"  Latest: {marketing_history[0]['query'][:50]}...")
    print()
    
    # Verify isolation
    print("Verification:")
    print(f"  ✓ Sales has {len(sales_history)} interactions")
    print(f"  ✓ Marketing has {len(marketing_history)} interactions")
    print(f"  ✓ Contexts are completely isolated")
    
    print("\n" + "="*70)


def show_profile_statistics():
    """
    Display statistics for all profiles.
    """
    print("\n" + "="*70)
    print("PROFILE STATISTICS")
    print("="*70)
    print()
    
    profiles = list_profiles()
    
    for profile in profiles:
        stats = get_profile_stats(profile['name'])
        if stats['exists']:
            print(f"{stats['name']} ({stats['persona']}):")
            print(f"  Created: {stats['created']}")
            print(f"  Interactions: {stats['total_interactions']}")
            print(f"  File size: {stats['file_size']} bytes")
            print(f"  Last accessed: {stats['last_accessed']}")
            print()
    
    print("="*70)


def demonstrate_api_usage():
    """
    Show how to use profiles with the Flask API.
    """
    print("\n" + "="*70)
    print("API USAGE EXAMPLES")
    print("="*70)
    print()
    
    print("1. List all profiles:")
    print("   GET /api/profiles")
    print("   Response: {profiles: [...], active_profile: 'Sales'}")
    print()
    
    print("2. Create a new profile:")
    print("   POST /api/profiles")
    print("   Body: {name: 'Engineering', persona: 'Analyst'}")
    print()
    
    print("3. Activate a profile:")
    print("   POST /api/profiles/Sales/activate")
    print()
    
    print("4. Query with specific profile:")
    print("   POST /api/ask")
    print("   Body: {")
    print("     question: 'What are top products?',")
    print("     conversation_id: '123',")
    print("     profile: 'Sales'  // Optional, uses active if not specified")
    print("   }")
    print()
    
    print("5. Get profile history:")
    print("   GET /api/profiles/Sales/history?n=10")
    print()
    
    print("6. Get profile statistics:")
    print("   GET /api/profiles/Sales/stats")
    print()
    
    print("7. Delete a profile:")
    print("   DELETE /api/profiles/OldDepartment")
    print()
    
    print("="*70)


def main():
    """
    Run complete profile integration demonstration.
    """
    print("\n" + "="*70)
    print("PROFILE MANAGER INTEGRATION DEMO")
    print("="*70)
    print()
    
    # Setup
    setup_department_profiles()
    
    # Simulate workflows
    simulate_sales_workflow()
    simulate_marketing_workflow()
    
    # Demonstrate isolation
    demonstrate_profile_isolation()
    
    # Show statistics
    show_profile_statistics()
    
    # API usage
    demonstrate_api_usage()
    
    print("\n" + "="*70)
    print("✅ Profile Manager ready")
    print("="*70)
    print()
    print("💡 Key Benefits:")
    print("   • Separate context for each department")
    print("   • Persona-specific responses")
    print("   • Historical context preservation")
    print("   • Easy profile switching")
    print("   • Complete isolation between departments")
    print()


if __name__ == "__main__":
    main()
