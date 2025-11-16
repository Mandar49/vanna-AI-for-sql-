"""
Executive Intelligence Layer - Voice Interface (Phase 4A)
Offline speech recognition and text-to-speech capabilities.
Uses local libraries for complete offline operation.
"""

import os
from pathlib import Path
from typing import Optional
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Audio directory
AUDIO_DIR = "./reports/audio"
Path(AUDIO_DIR).mkdir(parents=True, exist_ok=True)


def _ensure_audio_dir():
    """Ensure audio directory exists."""
    Path(AUDIO_DIR).mkdir(parents=True, exist_ok=True)
    return AUDIO_DIR


def transcribe_audio(audio_path: str) -> Optional[str]:
    """
    Transcribe audio file to text using Whisper (offline).
    
    Args:
        audio_path: Path to audio file (wav, mp3, etc.)
        
    Returns:
        Transcribed text or None if transcription fails
        
    Example:
        text = transcribe_audio("recording.wav")
        print(f"Transcribed: {text}")
    """
    try:
        import whisper
        
        # Load model (small.en for English, faster and offline)
        print("Loading Whisper model (this may take a moment on first run)...")
        model = whisper.load_model("base")  # base is a good balance
        
        # Transcribe
        print(f"Transcribing audio from: {audio_path}")
        result = model.transcribe(audio_path)
        
        text = result["text"].strip()
        print(f"✓ Transcription complete: {text[:100]}...")
        
        return text
        
    except ImportError:
        print("✗ Whisper not installed. Install with: pip install openai-whisper")
        return None
    except Exception as e:
        print(f"✗ Transcription error: {e}")
        return None


def speak_text(text: str, save_to_file: Optional[str] = None) -> bool:
    """
    Convert text to speech and play it (offline).
    
    Args:
        text: Text to speak
        save_to_file: Optional path to save audio file
        
    Returns:
        True if successful, False otherwise
        
    Example:
        speak_text("Hello, this is your AI assistant")
        speak_text("Report generated", save_to_file="./reports/audio/summary.wav")
    """
    try:
        import pyttsx3
        
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Configure voice properties
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Get available voices and use first one
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        
        # Save to file if requested
        if save_to_file:
            _ensure_audio_dir()
            engine.save_to_file(text, save_to_file)
            engine.runAndWait()
            print(f"✓ Audio saved to: {save_to_file}")
        else:
            # Speak directly
            engine.say(text)
            engine.runAndWait()
            print(f"✓ Speech output complete")
        
        return True
        
    except ImportError:
        print("✗ pyttsx3 not installed. Install with: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"✗ Speech error: {e}")
        return False


def record_and_transcribe(duration: int = 5) -> Optional[str]:
    """
    Record audio from microphone and transcribe it.
    
    Args:
        duration: Recording duration in seconds (default: 5)
        
    Returns:
        Transcribed text or None if recording/transcription fails
        
    Example:
        text = record_and_transcribe(duration=10)
        if text:
            print(f"You said: {text}")
    """
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np
        
        _ensure_audio_dir()
        
        # Recording parameters
        sample_rate = 16000  # Whisper works best with 16kHz
        temp_file = os.path.join(AUDIO_DIR, "temp_recording.wav")
        
        print(f"🎙 Recording for {duration} seconds...")
        print("   Speak now...")
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()  # Wait for recording to complete
        
        print("✓ Recording complete")
        
        # Save to temporary file
        sf.write(temp_file, recording, sample_rate)
        
        # Transcribe
        text = transcribe_audio(temp_file)
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return text
        
    except ImportError as e:
        print(f"✗ Required library not installed: {e}")
        print("   Install with: pip install sounddevice soundfile")
        return None
    except Exception as e:
        print(f"✗ Recording error: {e}")
        return None


def summarize_conversation(profile: str, speak: bool = True) -> Optional[str]:
    """
    Read recent context from a profile and generate/speak a summary.
    
    Args:
        profile: Profile name to summarize
        speak: Whether to speak the summary (default: True)
        
    Returns:
        Summary text or None if profile not found
        
    Example:
        summary = summarize_conversation("Sales", speak=True)
        print(summary)
    """
    try:
        from profile_manager import load_recent, get_profile_stats
        
        # Get profile stats
        stats = get_profile_stats(profile)
        if not stats['exists']:
            print(f"✗ Profile '{profile}' not found")
            return None
        
        # Load recent interactions
        recent = load_recent(profile, n=5)
        
        if not recent:
            summary = f"Profile {profile} has no recent interactions."
        else:
            # Build summary
            summary_parts = [
                f"Summary for {profile} profile.",
                f"Total interactions: {stats['total_interactions']}.",
                f"Recent activity:"
            ]
            
            for i, interaction in enumerate(recent[:3], 1):
                query = interaction['query'][:80]
                summary_parts.append(f"{i}. {query}")
            
            summary = " ".join(summary_parts)
        
        print(f"📊 Summary: {summary}")
        
        # Speak if requested
        if speak:
            # Save audio file
            audio_file = os.path.join(AUDIO_DIR, f"{profile}_summary.wav")
            speak_text(summary, save_to_file=audio_file)
        
        return summary
        
    except ImportError:
        print("✗ profile_manager not available")
        return None
    except Exception as e:
        print(f"✗ Summary error: {e}")
        return None


def record_command(duration: int = 5) -> Optional[str]:
    """
    Record a voice command from microphone.
    
    Args:
        duration: Recording duration in seconds (default: 5)
        
    Returns:
        Recorded audio file path or None if recording fails
        
    Example:
        audio_path = record_command(duration=5)
        if audio_path:
            text = transcribe_audio(audio_path)
    """
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np
        from datetime import datetime
        
        _ensure_audio_dir()
        
        # Recording parameters
        sample_rate = 16000  # Whisper works best with 16kHz
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_file = os.path.join(AUDIO_DIR, f"command_{timestamp}.wav")
        
        print(f"🎙 Recording command for {duration} seconds...")
        print("   Speak your command now...")
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()  # Wait for recording to complete
        
        print("✓ Recording complete")
        
        # Save to file
        sf.write(audio_file, recording, sample_rate)
        print(f"✓ Audio saved to: {audio_file}")
        
        return audio_file
        
    except ImportError as e:
        print(f"✗ Required library not installed: {e}")
        print("   Install with: pip install sounddevice soundfile")
        return None
    except Exception as e:
        print(f"✗ Recording error: {e}")
        return None


def transcribe_and_execute(audio_path: Optional[str] = None, 
                          profile: Optional[str] = None,
                          duration: int = 5,
                          speak_response: bool = True) -> dict:
    """
    Voice Command Router: Record (or use existing audio), transcribe, and execute command.
    
    This is the main voice-to-action pipeline:
    1. Record audio (if audio_path not provided)
    2. Transcribe speech to text
    3. Pass text to orchestrator.execute_command()
    4. Optionally speak the response
    
    Args:
        audio_path: Path to audio file (if None, will record new audio)
        profile: Optional profile context for command execution
        duration: Recording duration in seconds (default: 5)
        speak_response: Whether to speak the response (default: True)
        
    Returns:
        Dictionary with:
            - success: bool
            - transcribed_text: str or None
            - command_result: dict or None
            - message: str
            
    Example:
        # Record and execute
        result = transcribe_and_execute(duration=5, profile="Sales")
        
        # Use existing audio
        result = transcribe_and_execute(audio_path="command.wav")
        
        if result['success']:
            print(f"Command: {result['transcribed_text']}")
            print(f"Result: {result['command_result']['message']}")
    """
    result = {
        "success": False,
        "transcribed_text": None,
        "command_result": None,
        "message": ""
    }
    
    try:
        # Step 1: Get audio (record or use existing)
        if audio_path is None:
            print("\n" + "="*70)
            print("VOICE COMMAND ROUTER - Recording")
            print("="*70)
            audio_path = record_command(duration=duration)
            
            if audio_path is None:
                result["message"] = "Recording failed"
                return result
        else:
            if not os.path.exists(audio_path):
                result["message"] = f"Audio file not found: {audio_path}"
                return result
        
        # Step 2: Transcribe audio to text
        print("\n" + "="*70)
        print("VOICE COMMAND ROUTER - Transcription")
        print("="*70)
        
        transcribed_text = transcribe_audio(audio_path)
        
        if transcribed_text is None:
            result["message"] = "Transcription failed"
            return result
        
        result["transcribed_text"] = transcribed_text
        print(f"\n✓ Transcribed command: '{transcribed_text}'")
        
        # Step 3: Execute command via orchestrator
        print("\n" + "="*70)
        print("VOICE COMMAND ROUTER - Execution")
        print("="*70)
        
        try:
            from orchestrator import execute_command
            
            # Execute command with optional profile context
            command_result = execute_command(transcribed_text, profile=profile)
            
            result["command_result"] = command_result
            
            if command_result["status"] == "success":
                result["success"] = True
                result["message"] = f"Command executed successfully: {command_result['message']}"
                
                print(f"\n✓ Command executed: {command_result['message']}")
                
                # Speak response if requested
                if speak_response:
                    response_text = f"Command completed. {command_result['message']}"
                    print(f"\n🔊 Speaking response...")
                    speak_text(response_text)
                
            else:
                result["message"] = f"Command execution failed: {command_result['message']}"
                print(f"\n✗ Execution failed: {command_result['message']}")
                
                if speak_response:
                    speak_text(f"Command failed. {command_result['message']}")
        
        except ImportError:
            result["message"] = "Orchestrator not available"
            print(f"\n✗ {result['message']}")
        except Exception as e:
            result["message"] = f"Execution error: {str(e)}"
            print(f"\n✗ {result['message']}")
        
        return result
        
    except Exception as e:
        result["message"] = f"Voice command router error: {str(e)}"
        print(f"\n✗ {result['message']}")
        return result


def listen_for_command(profile: Optional[str] = None,
                      duration: int = 5,
                      speak_response: bool = True) -> dict:
    """
    Convenience function: Listen for voice command and execute it.
    
    This is a simplified interface to transcribe_and_execute() that always
    records new audio.
    
    Args:
        profile: Optional profile context
        duration: Recording duration in seconds (default: 5)
        speak_response: Whether to speak the response (default: True)
        
    Returns:
        Result dictionary from transcribe_and_execute()
        
    Example:
        # Listen and execute
        result = listen_for_command(profile="Sales", duration=5)
        
        if result['success']:
            print(f"You said: {result['transcribed_text']}")
            print(f"Result: {result['command_result']['message']}")
    """
    return transcribe_and_execute(
        audio_path=None,
        profile=profile,
        duration=duration,
        speak_response=speak_response
    )


def test_voice_capabilities():
    """
    Test voice interface capabilities.
    Returns dict with capability status.
    """
    capabilities = {
        "whisper_available": False,
        "pyttsx3_available": False,
        "sounddevice_available": False,
        "transcription": False,
        "speech": False,
        "recording": False,
        "command_routing": False
    }
    
    # Test Whisper
    try:
        import whisper
        capabilities["whisper_available"] = True
        print("✓ Whisper available")
    except ImportError:
        print("✗ Whisper not available (pip install openai-whisper)")
    
    # Test pyttsx3
    try:
        import pyttsx3
        capabilities["pyttsx3_available"] = True
        print("✓ pyttsx3 available")
    except ImportError:
        print("✗ pyttsx3 not available (pip install pyttsx3)")
    
    # Test sounddevice
    try:
        import sounddevice
        capabilities["sounddevice_available"] = True
        print("✓ sounddevice available")
    except ImportError:
        print("✗ sounddevice not available (pip install sounddevice soundfile)")
    
    # Test orchestrator
    try:
        from orchestrator import execute_command
        capabilities["command_routing"] = True
        print("✓ Orchestrator available")
    except ImportError:
        print("✗ Orchestrator not available")
    
    # Test transcription (if Whisper available)
    if capabilities["whisper_available"]:
        capabilities["transcription"] = True
    
    # Test speech (if pyttsx3 available)
    if capabilities["pyttsx3_available"]:
        capabilities["speech"] = True
    
    # Test recording (if sounddevice available)
    if capabilities["sounddevice_available"]:
        capabilities["recording"] = True
    
    return capabilities


if __name__ == "__main__":
    print("="*70)
    print("VOICE INTERFACE TEST")
    print("="*70)
    print()
    
    # Test capabilities
    print("1. Testing voice capabilities...")
    capabilities = test_voice_capabilities()
    print()
    
    # Test speech output
    if capabilities["speech"]:
        print("2. Testing speech output...")
        speak_text("Hello, this is your AI Business Intelligence Assistant. Voice interface is ready.")
        print()
    
    # Test audio directory
    print("3. Checking audio directory...")
    audio_dir = _ensure_audio_dir()
    print(f"   ✓ Audio directory: {audio_dir}")
    print()
    
    # Summary
    print("="*70)
    print("VOICE INTERFACE STATUS")
    print("="*70)
    print(f"Transcription (STT): {'✓ Ready' if capabilities['transcription'] else '✗ Not available'}")
    print(f"Speech (TTS): {'✓ Ready' if capabilities['speech'] else '✗ Not available'}")
    print(f"Recording: {'✓ Ready' if capabilities['recording'] else '✗ Not available'}")
    print(f"Command Routing: {'✓ Ready' if capabilities['command_routing'] else '✗ Not available'}")
    print()
    
    # Test voice command router (simulated)
    if capabilities["command_routing"]:
        print("4. Testing voice command router (simulated)...")
        print("   Simulating: 'list profiles'")
        
        # Simulate transcribed text execution
        from orchestrator import execute_command
        result = execute_command("list profiles")
        
        if result['status'] == 'success':
            print(f"   ✓ Command routing works: {result['message']}")
        print()
    
    if capabilities["speech"] or capabilities["transcription"]:
        print("="*70)
        print("🎙 Voice Interface ready")
        if capabilities["command_routing"]:
            print("✅ Voice Command Router enabled")
        print("="*70)
    else:
        print("="*70)
        print("⚠️  Voice Interface partially ready")
        print("   Install dependencies for full functionality:")
        print("   pip install openai-whisper pyttsx3 sounddevice soundfile")
        print("="*70)
