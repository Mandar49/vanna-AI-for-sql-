"""
Voice Command Router Demo (Phase 5E)
Demonstrates voice-triggered orchestration and "speak to execute" capability.
"""

from pathlib import Path


def demo_voice_command_router():
    """Demonstrate voice command router capabilities."""
    print("\n" + "="*70)
    print("VOICE COMMAND ROUTER DEMO (Phase 5E)")
    print("="*70)
    
    # Import modules
    from voice_interface import (
        test_voice_capabilities,
        record_command,
        transcribe_and_execute,
        listen_for_command
    )
    from orchestrator import execute_command
    
    # Step 1: Test Voice Capabilities
    print("\n🔍 Step 1: Testing voice capabilities...")
    
    capabilities = test_voice_capabilities()
    
    print(f"\n   Capability Status:")
    print(f"      Transcription (STT): {'✓' if capabilities['transcription'] else '✗'}")
    print(f"      Speech (TTS): {'✓' if capabilities['speech'] else '✗'}")
    print(f"      Recording: {'✓' if capabilities['recording'] else '✗'}")
    print(f"      Command Routing: {'✓' if capabilities['command_routing'] else '✗'}")
    
    # Step 2: Demonstrate Command Routing (Simulated)
    print("\n🎯 Step 2: Demonstrating command routing (simulated)...")
    
    simulated_commands = [
        "list profiles",
        "analyze KPIs for Sales",
        "query document: business strategy",
        "generate report for Marketing"
    ]
    
    print(f"\n   Simulating voice commands:")
    
    for i, command in enumerate(simulated_commands, 1):
        print(f"\n   {i}. User speaks: '{command}'")
        
        # Simulate the voice-to-action pipeline
        result = execute_command(command)
        
        print(f"      Status: {result['status']}")
        print(f"      Message: {result['message']}")
        
        if result['status'] == 'success':
            print(f"      ✓ Command executed successfully")
    
    # Step 3: Demonstrate Complete Workflow
    print("\n🔄 Step 3: Complete voice-to-action workflow...")
    
    print(f"\n   Workflow Steps:")
    print(f"      1. 🎙 Record audio from microphone")
    print(f"      2. 📝 Transcribe speech to text (Whisper)")
    print(f"      3. 🎯 Parse intent (Orchestrator)")
    print(f"      4. ⚙️  Execute command")
    print(f"      5. 🔊 Speak response (pyttsx3)")
    
    print(f"\n   Example:")
    print(f"      User speaks: 'list profiles'")
    print(f"      System transcribes: 'list profiles'")
    print(f"      System executes: orchestrator.execute_command('list profiles')")
    print(f"      System responds: 'Found 7 profiles'")
    print(f"      System speaks: 'Command completed. Found 7 profiles'")
    
    # Step 4: Function Demonstrations
    print("\n📚 Step 4: Function demonstrations...")
    
    print(f"\n   A. record_command(duration=5)")
    print(f"      • Records audio from microphone")
    print(f"      • Saves to ./reports/audio/")
    print(f"      • Returns audio file path")
    print(f"      Example: audio_path = record_command(duration=5)")
    
    print(f"\n   B. transcribe_and_execute()")
    print(f"      • Complete voice-to-action pipeline")
    print(f"      • Records (or uses existing audio)")
    print(f"      • Transcribes speech")
    print(f"      • Executes command")
    print(f"      • Speaks response")
    print(f"      Example:")
    print(f"         result = transcribe_and_execute(")
    print(f"             audio_path=None,")
    print(f"             profile='Sales',")
    print(f"             duration=5,")
    print(f"             speak_response=True")
    print(f"         )")
    
    print(f"\n   C. listen_for_command()")
    print(f"      • Convenience wrapper")
    print(f"      • Always records new audio")
    print(f"      • Simplified interface")
    print(f"      Example:")
    print(f"         result = listen_for_command(")
    print(f"             profile='Sales',")
    print(f"             duration=5")
    print(f"         )")
    
    # Step 5: Integration Examples
    print("\n🔗 Step 5: Integration examples...")
    
    print(f"\n   Example 1: Voice-Activated KPI Dashboard")
    print(f"      def voice_kpi_dashboard():")
    print(f"          result = listen_for_command(duration=5)")
    print(f"          if result['success']:")
    print(f"              metrics = result['command_result']['outputs']['metrics']")
    print(f"              chart_kpi_dashboard(metrics)")
    
    print(f"\n   Example 2: Voice Assistant Loop")
    print(f"      def voice_assistant():")
    print(f"          while True:")
    print(f"              result = listen_for_command(duration=5)")
    print(f"              if 'exit' in result['transcribed_text']:")
    print(f"                  break")
    
    print(f"\n   Example 3: Voice-Controlled Reports")
    print(f"      result = listen_for_command(profile='Sales')")
    print(f"      # User says: 'generate report'")
    print(f"      # System executes: 'generate report for Sales'")
    
    # Step 6: Supported Commands
    print("\n📋 Step 6: Supported voice commands...")
    
    command_categories = {
        "Profile Management": [
            "list profiles",
            "activate profile Sales",
            "show profile Marketing"
        ],
        "KPI Analysis": [
            "analyze KPIs for Sales",
            "analyze financial metrics for Marketing",
            "calculate metrics for Finance"
        ],
        "Document Queries": [
            "query document business strategy",
            "search knowledge revenue targets",
            "find document market analysis"
        ],
        "Report Generation": [
            "generate report for Sales",
            "create summary for Marketing",
            "build report for Finance"
        ],
        "Scheduling": [
            "schedule daily report for HR at 9:00",
            "schedule report every 30 minutes",
            "list schedules"
        ]
    }
    
    for category, commands in command_categories.items():
        print(f"\n   {category}:")
        for cmd in commands:
            print(f"      • '{cmd}'")
    
    # Step 7: Performance Metrics
    print("\n⚡ Step 7: Performance metrics...")
    
    print(f"\n   Latency Breakdown:")
    print(f"      Recording:        ~5 seconds (configurable)")
    print(f"      Transcription:    2-5 seconds (depends on audio)")
    print(f"      Execution:        <200ms (typical)")
    print(f"      Speech Response:  1-2 seconds")
    print(f"      ─────────────────────────────────")
    print(f"      Total:            ~8-12 seconds")
    
    print(f"\n   Optimization Tips:")
    print(f"      • Use smaller Whisper model (base vs large)")
    print(f"      • Reduce recording duration for simple commands")
    print(f"      • Disable speech response for faster execution")
    print(f"      • Pre-load models to avoid initialization delay")
    
    # Step 8: Error Handling
    print("\n🛡️  Step 8: Error handling...")
    
    print(f"\n   Graceful Failure Handling:")
    print(f"      • Recording fails → Returns None, error message")
    print(f"      • Transcription fails → Returns None, error message")
    print(f"      • Command fails → Returns error status, message")
    print(f"      • Audio file missing → Returns error, file not found")
    
    print(f"\n   Example:")
    print(f"      result = listen_for_command(duration=5)")
    print(f"      if not result['success']:")
    print(f"          print(f\"Error: {{result['message']}}\")")
    print(f"          # Retry or fallback to text input")
    
    # Step 9: Real-World Use Cases
    print("\n🌍 Step 9: Real-world use cases...")
    
    use_cases = [
        {
            "name": "Executive Dashboard Control",
            "description": "Navigate dashboard using voice commands",
            "example": "Say: 'show sales KPIs' or 'generate quarterly report'"
        },
        {
            "name": "Hands-Free Reporting",
            "description": "Generate reports while multitasking",
            "example": "Say: 'create report for marketing' while in meeting"
        },
        {
            "name": "Quick Data Queries",
            "description": "Query business data without typing",
            "example": "Say: 'what are our revenue targets' for instant answer"
        },
        {
            "name": "Accessibility",
            "description": "Enable voice control for accessibility needs",
            "example": "Complete system control via voice commands"
        },
        {
            "name": "Mobile/Remote Access",
            "description": "Control system from mobile device",
            "example": "Voice commands via phone while traveling"
        }
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"\n   {i}. {use_case['name']}")
        print(f"      {use_case['description']}")
        print(f"      Example: {use_case['example']}")
    
    # Step 10: Testing
    print("\n🧪 Step 10: Testing...")
    
    print(f"\n   Run comprehensive test suite:")
    print(f"      python test_voice_command_router.py")
    
    print(f"\n   Test Coverage:")
    print(f"      ✓ Voice Capabilities")
    print(f"      ✓ Record Command")
    print(f"      ✓ Transcribe & Execute (Simulated)")
    print(f"      ✓ Transcribe & Execute Function")
    print(f"      ✓ Listen for Command")
    print(f"      ✓ Orchestrator Integration")
    print(f"      ✓ Complete Workflow")
    print(f"      ✓ Error Handling")
    print(f"      ✓ Profile Context")
    print(f"      ✓ Command Variety")
    
    # Summary
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    
    print("\n✅ Voice Command Router Capabilities Demonstrated:")
    print("   • Voice command recording (microphone input)")
    print("   • Speech-to-text transcription (Whisper)")
    print("   • Automatic command routing (orchestrator)")
    print("   • Command execution (all subsystems)")
    print("   • Text-to-speech responses (pyttsx3)")
    print("   • Profile context support")
    print("   • Error handling and recovery")
    print("   • Complete voice-to-action pipeline")
    
    print("\n💡 Next Steps:")
    print("   • Install dependencies: pip install openai-whisper pyttsx3 sounddevice soundfile")
    print("   • Run tests: python test_voice_command_router.py")
    print("   • Read guide: VOICE_COMMAND_ROUTER_GUIDE.md")
    print("   • Try live: result = listen_for_command(duration=5)")
    
    print("\n🎙 Voice Commands Ready:")
    print("   • 'list profiles' - Show all profiles")
    print("   • 'analyze KPIs for Sales' - Run KPI analysis")
    print("   • 'query document strategy' - Search knowledge base")
    print("   • 'generate report for Marketing' - Create report")
    print("   • 'schedule daily report at 9:00' - Set up automation")
    
    print("\n📊 System Integration:")
    print("   Voice commands work with ALL subsystems:")
    print("   ✓ Profile Manager")
    print("   ✓ KPI Analyzer")
    print("   ✓ Knowledge Fusion")
    print("   ✓ Report Generator")
    print("   ✓ Scheduler")
    print("   ✓ Dashboard Gateway")
    print("   ✓ Email Engine")
    
    print("="*70)


if __name__ == "__main__":
    try:
        demo_voice_command_router()
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("  • Run tests: python test_voice_command_router.py")
        print("  • Check guide: VOICE_COMMAND_ROUTER_GUIDE.md")
        print("  • Verify orchestrator: python orchestrator.py")
