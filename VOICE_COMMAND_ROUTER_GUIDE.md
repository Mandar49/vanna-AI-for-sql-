# Voice Command Router Guide (Phase 5E)

## Overview

The Voice Command Router enables **voice-triggered orchestration** with "speak to execute" capability. It provides a complete voice-to-action pipeline that records speech, transcribes it to text, and automatically executes commands through the orchestrator.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│        VOICE COMMAND ROUTER (Phase 5E)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🎙 Voice Input                                         │
│      ↓                                                   │
│  📼 Record Audio (sounddevice)                          │
│      ↓                                                   │
│  📝 Transcribe (Whisper STT)                            │
│      ↓                                                   │
│  🎯 Parse Intent (Orchestrator)                         │
│      ↓                                                   │
│  ⚙️  Execute Command                                     │
│      ↓                                                   │
│  🔊 Speak Response (pyttsx3 TTS)                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Voice Command Recording**
- Record audio from microphone
- Configurable duration (default: 5 seconds)
- Saves to `./reports/audio/` directory
- 16kHz sample rate (optimized for Whisper)

### 2. **Speech-to-Text Transcription**
- Offline transcription using Whisper
- Multiple model sizes (base recommended)
- Supports various audio formats (WAV, MP3, etc.)

### 3. **Automatic Command Routing**
- Transcribed text passed to orchestrator
- Automatic intent parsing
- Profile context support
- Error handling

### 4. **Text-to-Speech Response**
- Speaks command results
- Configurable voice properties
- Optional audio file saving

## Installation

```bash
# Core dependencies (already included)
pip install pandas numpy

# Voice dependencies (optional but recommended)
pip install openai-whisper      # Speech-to-text
pip install pyttsx3              # Text-to-speech
pip install sounddevice          # Audio recording
pip install soundfile            # Audio file handling
```

**Note:** Voice dependencies are optional. The system works without them using simulated/text input.

## Core Functions

### 1. Record Command

```python
from voice_interface import record_command

# Record 5 seconds of audio
audio_path = record_command(duration=5)

if audio_path:
    print(f"Audio saved: {audio_path}")
```

**Parameters:**
- `duration` (int): Recording duration in seconds (default: 5)

**Returns:**
- Audio file path or None if recording fails

### 2. Transcribe and Execute

```python
from voice_interface import transcribe_and_execute

# Record, transcribe, and execute
result = transcribe_and_execute(
    audio_path=None,          # None = record new audio
    profile="Sales",          # Optional profile context
    duration=5,               # Recording duration
    speak_response=True       # Speak the result
)

if result['success']:
    print(f"Command: {result['transcribed_text']}")
    print(f"Result: {result['command_result']['message']}")
```

**Parameters:**
- `audio_path` (Optional[str]): Path to audio file (None = record new)
- `profile` (Optional[str]): Profile context for command
- `duration` (int): Recording duration in seconds (default: 5)
- `speak_response` (bool): Whether to speak response (default: True)

**Returns:**
```python
{
    "success": bool,
    "transcribed_text": str or None,
    "command_result": dict or None,
    "message": str
}
```

### 3. Listen for Command (Convenience Function)

```python
from voice_interface import listen_for_command

# Simplified interface - always records new audio
result = listen_for_command(
    profile="Sales",
    duration=5,
    speak_response=True
)

if result['success']:
    print(f"You said: {result['transcribed_text']}")
```

**Parameters:**
- `profile` (Optional[str]): Profile context
- `duration` (int): Recording duration (default: 5)
- `speak_response` (bool): Speak response (default: True)

## Usage Examples

### Example 1: Basic Voice Command

```python
from voice_interface import listen_for_command

# Listen for command and execute
print("Speak your command...")
result = listen_for_command(duration=5)

if result['success']:
    print(f"✓ Command executed: {result['command_result']['message']}")
else:
    print(f"✗ Failed: {result['message']}")
```

**User speaks:** "list profiles"  
**Output:**
```
🎙 Recording command for 5 seconds...
   Speak your command now...
✓ Recording complete
✓ Transcription complete: list profiles...
✓ Command executed: Found 7 profiles
🔊 Speaking response...
✓ Command executed: Found 7 profiles
```

### Example 2: Voice Command with Profile Context

```python
from voice_interface import listen_for_command

# Execute command in Sales profile context
result = listen_for_command(
    profile="Sales",
    duration=5,
    speak_response=True
)
```

**User speaks:** "analyze KPIs"  
**System:** Automatically adds profile context → "analyze KPIs for Sales"

### Example 3: Use Existing Audio File

```python
from voice_interface import transcribe_and_execute

# Transcribe and execute from existing audio
result = transcribe_and_execute(
    audio_path="./recordings/command.wav",
    speak_response=False
)

print(f"Transcribed: {result['transcribed_text']}")
print(f"Result: {result['command_result']}")
```

### Example 4: Batch Voice Commands

```python
from voice_interface import listen_for_command

commands_to_execute = 3

for i in range(commands_to_execute):
    print(f"\nCommand {i+1}/{commands_to_execute}")
    result = listen_for_command(duration=5)
    
    if result['success']:
        print(f"✓ {result['transcribed_text']}")
    else:
        print(f"✗ {result['message']}")
```

### Example 5: Voice-Activated Dashboard

```python
from voice_interface import listen_for_command
import time

def voice_dashboard():
    """Voice-activated executive dashboard."""
    print("Voice Dashboard Active")
    print("Say 'exit' to quit")
    
    while True:
        result = listen_for_command(duration=5, speak_response=True)
        
        if result['success']:
            text = result['transcribed_text'].lower()
            
            if 'exit' in text or 'quit' in text:
                print("Exiting voice dashboard...")
                break
            
            print(f"✓ Executed: {result['command_result']['message']}")
        
        time.sleep(1)

# Run voice dashboard
voice_dashboard()
```

## Supported Voice Commands

All orchestrator commands work via voice:

### Profile Management
- "list profiles"
- "activate profile Sales"
- "show profile Marketing"

### KPI Analysis
- "analyze KPIs for Sales"
- "analyze financial metrics for Marketing"
- "calculate metrics for Finance"

### Document Queries
- "query document business strategy"
- "search knowledge revenue targets"
- "find document market analysis"

### Report Generation
- "generate report for Sales"
- "create summary for Marketing"
- "build report for Finance"

### Scheduling
- "schedule daily report for HR at 9:00"
- "schedule report every 30 minutes"
- "list schedules"

### Other Commands
- "list reports"
- "summarize for Sales"
- "speak summary for Marketing"

## Integration Examples

### Integration 1: Voice-Activated KPI Dashboard

```python
from voice_interface import listen_for_command
from kpi_analyzer import analyze_kpis
from viz import chart_kpi_dashboard

def voice_kpi_dashboard():
    """Voice-activated KPI dashboard."""
    print("🎙 Voice KPI Dashboard")
    print("Say: 'analyze KPIs for [profile]'")
    
    result = listen_for_command(duration=5)
    
    if result['success']:
        # Get KPI data from command result
        if 'metrics' in result['command_result'].get('outputs', {}):
            metrics = result['command_result']['outputs']['metrics']
            
            # Generate dashboard
            chart_path = chart_kpi_dashboard(metrics)
            print(f"📊 Dashboard: {chart_path}")

voice_kpi_dashboard()
```

### Integration 2: Voice-Controlled Reports

```python
from voice_interface import listen_for_command

def voice_report_generator():
    """Generate reports via voice commands."""
    profiles = ["Sales", "Marketing", "Finance"]
    
    print("Available profiles:", ", ".join(profiles))
    print("Say: 'generate report for [profile]'")
    
    result = listen_for_command(duration=5)
    
    if result['success']:
        if result['command_result']['status'] == 'success':
            outputs = result['command_result']['outputs']
            print(f"✓ Report: {outputs.get('report_path')}")

voice_report_generator()
```

### Integration 3: Voice Assistant Loop

```python
from voice_interface import listen_for_command

def voice_assistant():
    """Continuous voice assistant."""
    print("🎙 Voice Assistant Active")
    print("Commands: list profiles, analyze KPIs, generate report, exit")
    
    while True:
        print("\nListening...")
        result = listen_for_command(duration=5, speak_response=True)
        
        if not result['success']:
            continue
        
        text = result['transcribed_text'].lower()
        
        if 'exit' in text or 'stop' in text:
            print("Goodbye!")
            break

voice_assistant()
```

### Integration 4: Scheduled Voice Reports

```python
from scheduler import schedule_daily
from voice_interface import transcribe_and_execute

def daily_voice_report():
    """Generate and speak daily report."""
    # Simulate voice command
    result = transcribe_and_execute(
        audio_path=None,  # Would use pre-recorded command
        profile="Sales",
        speak_response=True
    )
    
    if result['success']:
        print("✓ Daily voice report complete")

# Schedule daily at 9 AM
schedule_daily(9, 0, daily_voice_report)
```

## Testing

### Test Voice Capabilities

```python
from voice_interface import test_voice_capabilities

capabilities = test_voice_capabilities()

print(f"Transcription: {capabilities['transcription']}")
print(f"Speech: {capabilities['speech']}")
print(f"Recording: {capabilities['recording']}")
print(f"Command Routing: {capabilities['command_routing']}")
```

### Run Test Suite

```bash
python test_voice_command_router.py
```

**Test Coverage:**
- ✓ Voice Capabilities
- ✓ Record Command
- ✓ Transcribe & Execute (Simulated)
- ✓ Transcribe & Execute Function
- ✓ Listen for Command
- ✓ Orchestrator Integration
- ✓ Complete Workflow
- ✓ Error Handling
- ✓ Profile Context
- ✓ Command Variety

## Performance

### Latency Breakdown
- **Recording**: ~5 seconds (configurable)
- **Transcription**: ~2-5 seconds (depends on audio length and model)
- **Command Execution**: <200ms (typical)
- **Speech Response**: ~1-2 seconds
- **Total**: ~8-12 seconds for complete cycle

### Optimization Tips
1. Use smaller Whisper model (base or small)
2. Reduce recording duration for simple commands
3. Disable speech response for faster execution
4. Pre-load Whisper model to avoid initialization delay

## Troubleshooting

### Whisper Not Available

**Problem:**
```
✗ Whisper not installed
```

**Solution:**
```bash
pip install openai-whisper
```

### pyttsx3 Not Available

**Problem:**
```
✗ pyttsx3 not installed
```

**Solution:**
```bash
pip install pyttsx3
```

### Recording Fails

**Problem:**
```
✗ Recording error: No default input device
```

**Solution:**
- Check microphone is connected
- Verify microphone permissions
- Install: `pip install sounddevice soundfile`

### Transcription Fails

**Problem:**
```
✗ Transcription error
```

**Solution:**
- Ensure audio file is valid WAV format
- Check audio is not silent
- Try different Whisper model size

### Command Not Recognized

**Problem:**
```
Command executed: unknown - Status: error
```

**Solution:**
- Speak more clearly
- Use supported command phrases
- Check orchestrator intent parsing
- Add custom intent patterns

## Best Practices

### 1. Clear Speech
```python
# Give users guidance
print("Speak clearly: 'analyze KPIs for Sales'")
result = listen_for_command(duration=5)
```

### 2. Appropriate Duration
```python
# Short commands: 3-5 seconds
result = listen_for_command(duration=3)

# Complex commands: 7-10 seconds
result = listen_for_command(duration=10)
```

### 3. Error Handling
```python
result = listen_for_command(duration=5)

if not result['success']:
    print(f"Error: {result['message']}")
    # Retry or fallback to text input
```

### 4. Profile Context
```python
# Always provide profile context when relevant
result = listen_for_command(
    profile="Sales",  # Adds context
    duration=5
)
```

### 5. Feedback
```python
# Provide visual and audio feedback
print("🎙 Listening...")
result = listen_for_command(duration=5, speak_response=True)
print(f"✓ {result['transcribed_text']}")
```

## API Reference

### record_command(duration=5)
Record voice command from microphone.

**Returns:** Audio file path or None

### transcribe_and_execute(audio_path=None, profile=None, duration=5, speak_response=True)
Complete voice-to-action pipeline.

**Returns:** Dict with success, transcribed_text, command_result, message

### listen_for_command(profile=None, duration=5, speak_response=True)
Convenience function for recording and executing.

**Returns:** Dict with success, transcribed_text, command_result, message

### test_voice_capabilities()
Test available voice capabilities.

**Returns:** Dict with capability flags

## Summary

The Voice Command Router provides:

✅ **Voice Recording** - Microphone input with configurable duration  
✅ **Speech-to-Text** - Offline transcription with Whisper  
✅ **Command Routing** - Automatic orchestrator integration  
✅ **Text-to-Speech** - Spoken responses with pyttsx3  
✅ **Profile Context** - Profile-aware command execution  
✅ **Error Handling** - Graceful failure handling  
✅ **Complete Pipeline** - End-to-end voice-to-action  

**Storage:** Audio files in `./reports/audio/`  
**Dependencies:** openai-whisper, pyttsx3, sounddevice, soundfile (all optional)  
**Performance:** ~8-12 seconds total latency  

---

**Phase 5E Complete** ✅  
Next: Advanced voice features (wake words, continuous listening, multi-language)
