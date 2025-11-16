"""
Example: Voice Interface and Dashboard Integration
Demonstrates voice-activated queries and dashboard usage.
"""

from voice_interface import (
    speak_text,
    test_voice_capabilities,
    summarize_conversation
)
from profile_manager import init_profile, save_interaction, set_active_profile


def demo_voice_capabilities():
    """
    Demonstrate voice interface capabilities.
    """
    print("="*70)
    print("VOICE INTERFACE DEMO")
    print("="*70)
    print()
    
    # Test capabilities
    print("1. Testing voice capabilities...")
    capabilities = test_voice_capabilities()
    print()
    
    # Demo speech output
    if capabilities["speech"]:
        print("2. Demonstrating text-to-speech...")
        speak_text("Welcome to the Executive Intelligence Dashboard")
        speak_text("Voice interface is operational and ready for use")
        print("   ✓ Speech output demonstrated\n")
    else:
        print("2. Text-to-speech not available")
        print("   Install with: pip install pyttsx3\n")
    
    # Demo conversation summary
    print("3. Demonstrating conversation summary...")
    
    # Create sample profile with interactions
    init_profile("DemoSales", persona="Analyst")
    save_interaction(
        "DemoSales",
        "What are our top products?",
        "Top products: Widget A, Widget B, Widget C",
        sql="SELECT product, SUM(sales) FROM sales GROUP BY product"
    )
    save_interaction(
        "DemoSales",
        "Show quarterly revenue",
        "Q1: $1.2M, Q2: $1.5M, Q3: $1.8M, Q4: $2.1M",
        sql="SELECT quarter, SUM(revenue) FROM sales GROUP BY quarter"
    )
    
    # Generate summary (without speaking for demo)
    summary = summarize_conversation("DemoSales", speak=False)
    if summary:
        print(f"   Summary: {summary[:100]}...")
        print("   ✓ Summary generated\n")
    
    print("="*70)


def demo_dashboard_usage():
    """
    Demonstrate dashboard gateway usage.
    """
    print("\n" + "="*70)
    print("DASHBOARD GATEWAY DEMO")
    print("="*70)
    print()
    
    print("Dashboard Features:")
    print()
    
    print("1. Profile Management")
    print("   • View all department profiles")
    print("   • See interaction counts")
    print("   • Activate profiles with one click")
    print("   • Visual indication of active profile")
    print()
    
    print("2. Report Access")
    print("   • List recent reports")
    print("   • View reports in browser")
    print("   • See report metadata")
    print("   • Quick access to latest reports")
    print()
    
    print("3. Voice Controls")
    print("   • Generate voice summaries")
    print("   • Trigger report generation")
    print("   • Hands-free operation")
    print()
    
    print("4. System Status")
    print("   • Real-time statistics")
    print("   • Profile activity")
    print("   • System health")
    print()
    
    print("="*70)


def demo_integration_workflow():
    """
    Demonstrate complete integration workflow.
    """
    print("\n" + "="*70)
    print("INTEGRATION WORKFLOW DEMO")
    print("="*70)
    print()
    
    print("Scenario: Executive Morning Briefing")
    print()
    
    # Step 1: Setup profiles
    print("Step 1: Initialize department profiles...")
    departments = ["Sales", "Marketing", "Finance"]
    for dept in departments:
        init_profile(dept, persona="Analyst")
    print("   ✓ Profiles initialized\n")
    
    # Step 2: Activate profile
    print("Step 2: Activate Sales profile...")
    set_active_profile("Sales")
    print("   ✓ Sales profile active\n")
    
    # Step 3: Add sample interactions
    print("Step 3: Record recent interactions...")
    interactions = [
        ("What are yesterday's sales?", "Total sales: $125,000 (up 15% from previous day)"),
        ("Top performing region?", "North region leads with $45,000 in sales"),
        ("Any issues to address?", "Inventory low on Widget A, restock recommended")
    ]
    
    for query, response in interactions:
        save_interaction("Sales", query, response, sql="SELECT ...")
    print(f"   ✓ {len(interactions)} interactions recorded\n")
    
    # Step 4: Generate voice summary
    print("Step 4: Generate executive briefing...")
    capabilities = test_voice_capabilities()
    
    if capabilities["speech"]:
        print("   🎙 Speaking summary...")
        summarize_conversation("Sales", speak=True)
        print("   ✓ Voice briefing complete\n")
    else:
        print("   ⚠ Voice output not available")
        summary = summarize_conversation("Sales", speak=False)
        print(f"   Text summary: {summary}\n")
    
    # Step 5: Dashboard access
    print("Step 5: Access dashboard...")
    print("   📊 Dashboard URL: http://127.0.0.1:5000/dashboard/")
    print("   ✓ Dashboard provides:")
    print("      • Visual profile overview")
    print("      • Recent reports list")
    print("      • One-click report generation")
    print("      • Voice summary controls")
    print()
    
    print("="*70)


def demo_api_usage():
    """
    Demonstrate API usage examples.
    """
    print("\n" + "="*70)
    print("API USAGE EXAMPLES")
    print("="*70)
    print()
    
    print("Voice Interface API:")
    print()
    
    print("1. Text-to-Speech:")
    print("   from voice_interface import speak_text")
    print("   speak_text('Hello, this is your AI assistant')")
    print()
    
    print("2. Speech-to-Text:")
    print("   from voice_interface import transcribe_audio")
    print("   text = transcribe_audio('recording.wav')")
    print()
    
    print("3. Record and Transcribe:")
    print("   from voice_interface import record_and_transcribe")
    print("   text = record_and_transcribe(duration=5)")
    print()
    
    print("4. Conversation Summary:")
    print("   from voice_interface import summarize_conversation")
    print("   summary = summarize_conversation('Sales', speak=True)")
    print()
    
    print("Dashboard Gateway API:")
    print()
    
    print("1. Access Dashboard:")
    print("   GET http://127.0.0.1:5000/dashboard/")
    print()
    
    print("2. List Reports:")
    print("   GET http://127.0.0.1:5000/dashboard/reports")
    print()
    
    print("3. Speak Summary:")
    print("   GET http://127.0.0.1:5000/dashboard/speak_summary?profile=Sales")
    print()
    
    print("4. Generate Report:")
    print("   GET http://127.0.0.1:5000/dashboard/run_report?profile=Sales")
    print()
    
    print("="*70)


def main():
    """
    Run complete voice and dashboard demonstration.
    """
    print("\n" + "="*70)
    print("VOICE INTERFACE & DASHBOARD INTEGRATION")
    print("="*70)
    print()
    
    # Demo voice capabilities
    demo_voice_capabilities()
    
    # Demo dashboard usage
    demo_dashboard_usage()
    
    # Demo integration workflow
    demo_integration_workflow()
    
    # Demo API usage
    demo_api_usage()
    
    print("\n" + "="*70)
    print("✅ Voice Interface & Dashboard ready")
    print("="*70)
    print()
    
    print("💡 Quick Start:")
    print("   1. Start Flask app: python ad_ai_app.py")
    print("   2. Open dashboard: http://127.0.0.1:5000/dashboard/")
    print("   3. Activate a profile")
    print("   4. Click 'Speak Summary' for voice briefing")
    print("   5. Click 'Generate Report' for instant report")
    print()
    
    print("📦 Optional Dependencies:")
    print("   • pip install pyttsx3 (for text-to-speech)")
    print("   • pip install openai-whisper (for speech-to-text)")
    print("   • pip install sounddevice soundfile (for recording)")
    print()


if __name__ == "__main__":
    main()
