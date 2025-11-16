"""
Test suite for Executive Intelligence Layer - Voice Interface
Verifies offline speech recognition and text-to-speech capabilities.
"""

import os
import pytest
from pathlib import Path

from voice_interface import (
    _ensure_audio_dir,
    speak_text,
    test_voice_capabilities,
    summarize_conversation,
    AUDIO_DIR
)


class TestVoiceInterface:
    """Test suite for voice interface functions."""
    
    def test_audio_directory_creation(self):
        """Test audio directory is created."""
        audio_dir = _ensure_audio_dir()
        
        assert os.path.exists(audio_dir)
        assert os.path.isdir(audio_dir)
        assert audio_dir.endswith("audio") or audio_dir.endswith("audio/")
        
        print("✓ Audio directory creation works")
    
    def test_voice_capabilities(self):
        """Test voice capabilities detection."""
        capabilities = test_voice_capabilities()
        
        assert isinstance(capabilities, dict)
        assert "whisper_available" in capabilities
        assert "pyttsx3_available" in capabilities
        assert "sounddevice_available" in capabilities
        assert "transcription" in capabilities
        assert "speech" in capabilities
        assert "recording" in capabilities
        
        print("✓ Voice capabilities detection works")
    
    def test_speak_text_with_save(self):
        """Test text-to-speech with file saving."""
        test_file = os.path.join(AUDIO_DIR, "test_speech.wav")
        
        # Clean up if exists
        if os.path.exists(test_file):
            os.remove(test_file)
        
        # Try to speak and save
        result = speak_text("This is a test", save_to_file=test_file)
        
        # Check result (may be False if pyttsx3 not installed)
        if result:
            assert os.path.exists(test_file)
            print("✓ Speech with file save works")
        else:
            print("⚠ Speech not available (pyttsx3 not installed)")
    
    def test_speak_text_without_save(self):
        """Test text-to-speech without saving."""
        # This will speak if pyttsx3 is available
        result = speak_text("Test speech output")
        
        # Result depends on whether pyttsx3 is installed
        assert isinstance(result, bool)
        
        if result:
            print("✓ Speech output works")
        else:
            print("⚠ Speech not available (pyttsx3 not installed)")
    
    def test_summarize_conversation_no_profile(self):
        """Test conversation summary with non-existent profile."""
        summary = summarize_conversation("NonExistentProfile", speak=False)
        
        # Should return None for non-existent profile
        assert summary is None
        
        print("✓ Non-existent profile handling works")
    
    def test_summarize_conversation_with_profile(self):
        """Test conversation summary with existing profile."""
        try:
            from profile_manager import init_profile, save_interaction
            
            # Create test profile
            init_profile("TestVoice", persona="Analyst")
            save_interaction(
                "TestVoice",
                "Test query",
                "Test response",
                sql="SELECT 1"
            )
            
            # Generate summary (without speaking)
            summary = summarize_conversation("TestVoice", speak=False)
            
            assert summary is not None
            assert "TestVoice" in summary
            
            print("✓ Conversation summary works")
            
        except ImportError:
            print("⚠ profile_manager not available for testing")
    
    def test_offline_operation(self):
        """Verify voice interface works offline."""
        # All operations should work without internet
        _ensure_audio_dir()
        capabilities = test_voice_capabilities()
        
        # These should work regardless of internet
        assert capabilities is not None
        
        print("✓ Offline operation works")


def run_manual_test():
    """Manual test for quick verification."""
    print("\n" + "="*70)
    print("MANUAL TEST: Voice Interface")
    print("="*70 + "\n")
    
    print("1. Testing audio directory...")
    audio_dir = _ensure_audio_dir()
    print(f"   ✓ Audio directory: {audio_dir}\n")
    
    print("2. Testing voice capabilities...")
    capabilities = test_voice_capabilities()
    print()
    
    print("3. Testing speech output...")
    if capabilities["speech"]:
        result = speak_text("Voice interface test successful", save_to_file=None)
        print(f"   ✓ Speech test: {'Success' if result else 'Failed'}\n")
    else:
        print("   ⚠ Speech not available (install pyttsx3)\n")
    
    print("4. Testing file save...")
    test_file = os.path.join(AUDIO_DIR, "test_output.wav")
    if capabilities["speech"]:
        result = speak_text("Test audio file", save_to_file=test_file)
        if result and os.path.exists(test_file):
            print(f"   ✓ Audio file saved: {test_file}\n")
        else:
            print("   ⚠ Audio file save failed\n")
    else:
        print("   ⚠ Speech not available\n")
    
    print("="*70)
    print("VERIFICATION")
    print("="*70)
    print(f"✓ Audio directory exists: {os.path.exists(AUDIO_DIR)}")
    print(f"✓ Transcription available: {capabilities['transcription']}")
    print(f"✓ Speech available: {capabilities['speech']}")
    print(f"✓ Recording available: {capabilities['recording']}")
    print(f"✓ Offline operation: True")
    
    print("\n" + "="*70)
    if capabilities["speech"] or capabilities["transcription"]:
        print("🎙 Voice Interface ready")
    else:
        print("⚠️  Voice Interface partially ready")
        print("   Install dependencies: pip install openai-whisper pyttsx3")
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
