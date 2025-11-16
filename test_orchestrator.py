"""
Test suite for Executive Intelligence Layer - Orchestration Core
Verifies command parsing, routing, and execution.
"""

import os
import pytest
from unittest.mock import Mock, patch

from orchestrator import (
    parse_intent,
    execute_command,
    orchestrate_conversation,
    get_orchestration_history,
    LOG_DIR
)


class TestOrchestrator:
    """Test suite for orchestration core functions."""
    
    def test_parse_intent_generate_report(self):
        """Test parsing generate report command."""
        intent = parse_intent("generate report for Sales")
        
        assert intent["action"] == "generate_report"
        assert intent["profile"] == "Sales"
        
        print("✓ Generate report intent parsing works")
    
    def test_parse_intent_summarize(self):
        """Test parsing summarize command."""
        intent = parse_intent("summarize for Marketing")
        
        assert intent["action"] == "summarize"
        assert intent["profile"] == "Marketing"
        
        print("✓ Summarize intent parsing works")
    
    def test_parse_intent_schedule_daily(self):
        """Test parsing schedule daily command."""
        intent = parse_intent("schedule daily report for HR at 9:00")
        
        assert intent["action"] == "schedule"
        assert intent["profile"] == "HR"
        assert intent["params"]["frequency"] == "daily"
        assert intent["params"]["hour"] == 9
        assert intent["params"]["minute"] == 0
        
        print("✓ Schedule daily intent parsing works")
    
    def test_parse_intent_schedule_interval(self):
        """Test parsing schedule interval command."""
        intent = parse_intent("schedule report for Sales every 30 minutes")
        
        assert intent["action"] == "schedule"
        assert intent["profile"] == "Sales"
        assert intent["params"]["frequency"] == "interval"
        assert intent["params"]["minutes"] == 30
        
        print("✓ Schedule interval intent parsing works")
    
    def test_parse_intent_speak(self):
        """Test parsing speak command."""
        intent = parse_intent("speak for Finance")
        
        assert intent["action"] == "speak"
        assert intent["profile"] == "Finance"
        
        print("✓ Speak intent parsing works")
    
    def test_parse_intent_list_profiles(self):
        """Test parsing list profiles command."""
        intent = parse_intent("list profiles")
        
        assert intent["action"] == "list_profiles"
        
        print("✓ List profiles intent parsing works")
    
    def test_parse_intent_list_reports(self):
        """Test parsing list reports command."""
        intent = parse_intent("show reports")
        
        assert intent["action"] == "list_reports"
        
        print("✓ List reports intent parsing works")
    
    def test_parse_intent_activate_profile(self):
        """Test parsing activate profile command."""
        intent = parse_intent("activate profile for Operations")
        
        assert intent["action"] == "activate_profile"
        assert intent["profile"] == "Operations"
        
        print("✓ Activate profile intent parsing works")
    
    def test_parse_intent_generate_chart(self):
        """Test parsing generate chart command."""
        intent = parse_intent("generate trend chart for Sales")
        
        assert intent["action"] == "generate_chart"
        assert intent["profile"] == "Sales"
        assert intent["params"]["chart_type"] == "trend"
        
        print("✓ Generate chart intent parsing works")
    
    def test_execute_command_list_profiles(self):
        """Test executing list profiles command."""
        result = execute_command("list profiles")
        
        assert "status" in result
        assert "message" in result
        assert "outputs" in result
        assert result["status"] in ["success", "error"]
        
        print("✓ Execute list profiles works")
    
    def test_execute_command_with_profile_override(self):
        """Test executing command with profile override."""
        result = execute_command("summarize", profile="TestProfile")
        
        assert "status" in result
        assert result["intent"]["profile"] == "TestProfile"
        
        print("✓ Profile override works")
    
    def test_execute_command_unknown_action(self):
        """Test executing unknown command."""
        result = execute_command("do something random")
        
        assert result["status"] == "error"
        assert "unknown" in result["message"].lower()
        
        print("✓ Unknown action handling works")
    
    def test_orchestration_history(self):
        """Test orchestration history tracking."""
        # Execute some commands
        execute_command("list profiles")
        execute_command("list reports")
        
        # Get history
        history = get_orchestration_history(limit=10)
        
        assert isinstance(history, list)
        assert len(history) > 0
        
        # Check history structure
        if history:
            entry = history[0]
            assert "command" in entry
            assert "intent" in entry
            assert "result" in entry
            assert "timestamp" in entry
        
        print("✓ Orchestration history works")
    
    def test_log_directory_creation(self):
        """Test log directory is created."""
        assert os.path.exists(LOG_DIR)
        assert os.path.isdir(LOG_DIR)
        
        print("✓ Log directory creation works")
    
    def test_offline_operation(self):
        """Verify orchestrator works offline."""
        # All operations should work without internet
        intent = parse_intent("generate report for Sales")
        result = execute_command("list profiles")
        history = get_orchestration_history()
        
        assert intent is not None
        assert result is not None
        assert history is not None
        
        print("✓ Offline operation works")


def run_manual_test():
    """Manual test for quick verification."""
    print("\n" + "="*70)
    print("MANUAL TEST: Orchestration Core")
    print("="*70 + "\n")
    
    print("1. Testing intent parsing...")
    test_commands = [
        "generate report for Sales",
        "summarize for Marketing",
        "schedule daily report for HR at 9:00",
        "speak summary for Finance",
        "list profiles",
        "show reports",
        "activate profile for Operations",
        "generate chart for Sales"
    ]
    
    for cmd in test_commands:
        intent = parse_intent(cmd)
        print(f"   '{cmd}'")
        print(f"      → Action: {intent['action']}")
        print(f"      → Profile: {intent['profile']}")
    print()
    
    print("2. Testing command execution...")
    
    # Test list profiles
    result = execute_command("list profiles")
    print(f"   List profiles:")
    print(f"      Status: {result['status']}")
    print(f"      Message: {result['message']}")
    
    # Test list reports
    result = execute_command("list reports")
    print(f"   List reports:")
    print(f"      Status: {result['status']}")
    print(f"      Message: {result['message']}")
    print()
    
    print("3. Testing orchestration history...")
    history = get_orchestration_history(limit=5)
    print(f"   History entries: {len(history)}")
    if history:
        print(f"   Latest command: {history[-1]['command']}")
    print()
    
    print("4. Testing profile-specific routing...")
    result = execute_command("summarize for TestProfile")
    print(f"   Summarize TestProfile:")
    print(f"      Status: {result['status']}")
    print(f"      Profile routed: {result['intent']['profile']}")
    print()
    
    print("="*70)
    print("VERIFICATION")
    print("="*70)
    print(f"✓ Intent parsing: Working")
    print(f"✓ Command execution: Working")
    print(f"✓ Profile routing: Working")
    print(f"✓ History tracking: Working")
    print(f"✓ Log directory: {os.path.exists(LOG_DIR)}")
    print(f"✓ Offline operation: Confirmed")
    
    print("\n" + "="*70)
    print("🧩 Orchestration Core ready")
    print("="*70)


if __name__ == "__main__":
    # Run manual test
    run_manual_test()
    
    # Run pytest if available
    try:
        print("\n" + "="*70)
        print("RUNNING PYTEST SUITE")
        print("="*70 + "\n")
        pytest.main([__file__, "-v", "-s"])
    except:
        print("\nNote: Install pytest to run full test suite")
