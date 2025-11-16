# Executive Intelligence Layer - Voice Interface & Dashboard (Phase 4A)

## Overview

Phase 4A introduces an offline voice interface and executive dashboard gateway, enabling speech-based interaction and a centralized web interface for managing the AI BI Agent.

## Components

### 1. Voice Interface (`voice_interface.py`)

Offline speech recognition and text-to-speech capabilities using local libraries.

**Features:**
- Speech-to-Text (STT) using Whisper
- Text-to-Speech (TTS) using pyttsx3
- Audio recording from microphone
- Conversation summarization with voice output
- Fully offline operation

### 2. Dashboard Gateway (`dashboard_gateway.py`)

Minimal offline web dashboard providing executive-level access to the system.

**Features:**
- Profile management interface
- Recent reports listing
- Voice summary generation
- Manual report triggering
- Real-time system status

## Installation

### Core Dependencies (Required)

```bash
pip install flask pandas
```

### Voice Dependencies (Optional)

```bash
# For speech-to-text
pip install openai-whisper

# For text-to-speech
pip install pyttsx3

# For audio recording
pip install sounddevice soundfile
```

**Note:** Voice features work independently. Install only what you need.

## Voice Interface API

### Core Functions

#### `transcribe_audio(audio_path)`

Transcribe audio file to text using Whisper.

**Parameters:**
- `audio_path` (str): Path to audio file (wav, mp3, etc.)

**Returns:** Transcribed text or None

**Example:**
```python
from voice_interface import transcribe_audio

text = transcribe_audio("recording.wav")
print(f"Transcribed: {text}")
```

#### `speak_text(text, save_to_file=None)`

Convert text to speech and play it.

**Parameters:**
- `text` (str): Text to speak
- `save_to_file` (str, optional): Path to save audio file

**Returns:** True if successful

**Example:**
```python
from voice_interface import speak_text

# Speak directly
speak_text("Hello, this is your AI assistant")

# Save to file
speak_text("Report generated", save_to_file="./reports/audio/summary.wav")
```

#### `record_and_transcribe(duration=5)`

Record audio from microphone and transcribe it.

**Parameters:**
- `duration` (int): Recording duration in seconds

**Returns:** Transcribed text or None

**Example:**
```python
from voice_interface import record_and_transcribe

text = record_and_transcribe(duration=10)
if text:
    print(f"You said: {text}")
```

#### `summarize_conversation(profile, speak=True)`

Generate and speak a profile summary.

**Parameters:**
- `profile` (str): Profile name
- `speak` (bool): Whether to speak the summary

**Returns:** Summary text or None

**Example:**
```python
from voice_interface import summarize_conversation

summary = summarize_conversation("Sales", speak=True)
print(summary)
```

#### `test_voice_capabilities()`

Test which voice features are available.

**Returns:** Dictionary with capability status

**Example:**
```python
from voice_interface import test_voice_capabilities

capabilities = test_voice_capabilities()
print(f"Speech available: {capabilities['speech']}")
print(f"Transcription available: {capabilities['transcription']}")
```

## Dashboard Gateway API

### Flask Endpoints

#### `GET /dashboard/`

Main dashboard view showing profiles, reports, and system status.

**Response:** HTML dashboard page

**Example:**
```
http://127.0.0.1:5000/dashboard/
```

#### `GET /dashboard/reports`

List all available reports.

**Response:**
```json
{
  "success": true,
  "reports": [
    {
      "name": "sales_report_20241111.html",
      "path": "./reports/sales_report_20241111.html",
      "date": "2024-11-11 13:45",
      "size": 15360,
      "type": "HTML"
    }
  ]
}
```

#### `GET /dashboard/speak_summary?profile=<name>`

Generate and speak a profile summary.

**Parameters:**
- `profile` (query): Profile name

**Response:**
```json
{
  "success": true,
  "message": "Summary generated for Sales",
  "summary": "Summary for Sales profile..."
}
```

**Example:**
```
http://127.0.0.1:5000/dashboard/speak_summary?profile=Sales
```

#### `GET /dashboard/run_report?profile=<name>`

Manually trigger report generation for a profile.

**Parameters:**
- `profile` (query): Profile name

**Response:**
```json
{
  "success": true,
  "message": "Report generated for Sales",
  "report_path": "./reports/sales_summary_20241111.html"
}
```

**Example:**
```
http://127.0.0.1:5000/dashboard/run_report?profile=Sales
```

## Integration with Flask App

The dashboard is automatically integrated into `ad_ai_app.py`:

```python
# In ad_ai_app.py
from dashboard_gateway import dashboard_bp
app.register_blueprint(dashboard_bp)
```

Start the Flask app:

```bash
python ad_ai_app.py
```

Access the dashboard:

```
http://127.0.0.1:5000/dashboard/
```

## Use Cases

### 1. Voice-Activated Queries

```python
from voice_interface import record_and_transcribe

# Record user query
query = record_and_transcribe(duration=5)

# Process query through AI BI Agent
# ... (existing query processing)

# Speak response
speak_text(response)
```

### 2. Executive Briefings

```python
from voice_interface import summarize_conversation

# Generate voice summary for executive
summary = summarize_conversation("Sales", speak=True)

# Summary is also saved to ./reports/audio/Sales_summary.wav
```

### 3. Dashboard Monitoring

```
1. Open dashboard: http://127.0.0.1:5000/dashboard/
2. View active profile and system status
3. Click profile to activate
4. Click "Speak Summary" for voice briefing
5. Click "Generate Report" for instant report
```

### 4. Hands-Free Operation

```python
# Voice-only workflow
query = record_and_transcribe(duration=10)
response = process_query(query)  # Your processing logic
speak_text(response)
```

## Dashboard Features

### Profile Management

- View all department profiles
- See interaction counts
- Activate profiles with one click
- Visual indication of active profile

### Report Access

- List recent reports (HTML and Markdown)
- View reports in browser
- See report metadata (date, size, type)
- Quick access to latest reports

### Voice Controls

- Generate voice summaries
- Trigger report generation
- Hands-free operation support

### System Status

- Real-time profile statistics
- Total reports count
- System operational status
- Offline mode indicator

## Configuration

### Audio Directory

Audio files are saved to:

```
./reports/audio/
├── Sales_summary.wav
├── Marketing_summary.wav
└── temp_recording.wav
```

### Voice Models

**Whisper Models:**
- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: Better accuracy
- `medium`: High accuracy
- `large`: Best accuracy, slowest

Change model in `voice_interface.py`:

```python
model = whisper.load_model("base")  # Change to "small", "medium", etc.
```

### TTS Settings

Configure speech properties in `voice_interface.py`:

```python
engine.setProperty('rate', 150)     # Speed (words per minute)
engine.setProperty('volume', 0.9)   # Volume (0.0 to 1.0)
```

## Testing

### Voice Interface Tests

```bash
python test_voice_interface.py
```

**Tests:**
- Audio directory creation
- Voice capabilities detection
- Speech output
- File saving
- Conversation summarization
- Offline operation

### Dashboard Tests

```bash
python test_dashboard_gateway.py
```

**Tests:**
- Dashboard home endpoint
- Reports listing endpoint
- Speak summary endpoint
- Run report endpoint
- Blueprint registration

## Troubleshooting

### Voice Features Not Working

**Problem:** "pyttsx3 not installed"

**Solution:**
```bash
pip install pyttsx3
```

**Problem:** "Whisper not installed"

**Solution:**
```bash
pip install openai-whisper
```

**Problem:** "sounddevice not installed"

**Solution:**
```bash
pip install sounddevice soundfile
```

### Dashboard Not Accessible

**Problem:** Dashboard returns 404

**Solution:** Ensure blueprint is registered in `ad_ai_app.py`:
```python
from dashboard_gateway import dashboard_bp
app.register_blueprint(dashboard_bp)
```

**Problem:** Dashboard shows no profiles

**Solution:** Create profiles first:
```python
from profile_manager import init_profile
init_profile("Sales", persona="Analyst")
```

### Audio Recording Issues

**Problem:** No microphone detected

**Solution:**
- Check microphone is connected
- Grant microphone permissions
- Test with: `python -m sounddevice`

**Problem:** Recording quality poor

**Solution:** Adjust sample rate in `voice_interface.py`:
```python
sample_rate = 44100  # Higher quality (default: 16000)
```

## Performance

### Voice Processing

- **Transcription (base model)**: 1-3 seconds per 10 seconds of audio
- **Speech synthesis**: <1 second for typical responses
- **Recording**: Real-time (no delay)

### Dashboard

- **Page load**: <100ms
- **Report listing**: <50ms
- **Profile switching**: <10ms

## Limitations

### Current

- Voice features require optional dependencies
- Dashboard is read-only (no inline editing)
- No real-time audio streaming
- Single language support (English)

### Not Limitations

- ✅ Works completely offline
- ✅ No cloud services required
- ✅ No API keys needed
- ✅ Privacy-preserving (local processing)

## Security

### Data Privacy

- All voice processing happens locally
- No audio sent to external services
- No cloud API calls
- Complete data sovereignty

### Access Control

- Dashboard accessible only on localhost by default
- No authentication (add if needed)
- Profile isolation maintained

## Future Enhancements (Phase 4B+)

- Multi-language support
- Real-time audio streaming
- Voice command recognition
- Dashboard authentication
- Mobile-responsive design
- Dark mode
- Report scheduling from dashboard
- Profile creation from dashboard
- Inline report editing

## Examples

See `example_voice_dashboard.py` for complete examples including:
- Voice-activated queries
- Executive briefings
- Dashboard automation
- Integration patterns

## License

Same as parent project.

## Support

For issues or questions, refer to the main project documentation.
