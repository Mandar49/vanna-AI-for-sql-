# Executive Intelligence Layer - Orchestration Core (Phase 4B)

## Overview

The Orchestration Core is the central command layer that unifies all subsystems (profiles, scheduler, reports, voice, dashboard) into one intelligent command engine. It interprets user intents and routes them to appropriate modules for execution.

## Features

✅ **Intent Parsing**: Natural language command interpretation  
✅ **Unified Routing**: Single entry point for all operations  
✅ **Profile-Aware**: Context-sensitive command execution  
✅ **History Tracking**: Complete audit trail of all commands  
✅ **Error Handling**: Graceful failure recovery  
✅ **Offline Operation**: No external dependencies  
✅ **Extensible**: Easy to add new command types

## Architecture

```
User Command
     ↓
parse_intent() → Extract action, profile, parameters
     ↓
execute_command() → Route to appropriate handler
     ↓
┌────────────────────────────────────────┐
│  _handle_generate_report()             │
│  _handle_summarize()                   │
│  _handle_schedule()                    │
│  _handle_speak()                       │
│  _handle_list_profiles()               │
│  _handle_list_reports()                │
│  _handle_list_schedules()              │
│  _handle_activate_profile()            │
│  _handle_generate_chart()              │
└────────────────────────────────────────┘
     ↓
Result + History Logging
```

## API Reference

### Core Functions

#### `parse_intent(text)`

Parse user command to extract intent, action, profile, and parameters.

**Parameters:**
- `text` (str): User command text

**Returns:** Dictionary with parsed intent

**Example:**
```python
from orchestrator import parse_intent

intent = parse_intent("generate report for Sales")
# Returns: {
#   "action": "generate_report",
#   "profile": "Sales",
#   "params": {},
#   "raw_text": "generate report for Sales"
# }
```

**Supported Actions:**
- `generate_report` - Generate executive report
- `summarize` - Create profile summary
- `schedule` - Schedule recurring job
- `speak` - Voice output
- `list_profiles` - List all profiles
- `list_reports` - List all reports
- `list_schedules` - List scheduled jobs
- `activate_profile` - Switch active profile
- `generate_chart` - Create visualization

#### `execute_command(command, profile=None)`

Execute a command by routing to appropriate subsystems.

**Parameters:**
- `command` (str): User command text
- `profile` (str, optional): Profile to use (overrides parsed profile)

**Returns:** Result dictionary with status, message, and outputs

**Example:**
```python
from orchestrator import execute_command

result = execute_command("generate report for Sales")
print(result["status"])    # "success" or "error"
print(result["message"])   # Human-readable message
print(result["outputs"])   # Command outputs (paths, data, etc.)
```

**Result Structure:**
```python
{
    "status": "success",           # or "error"
    "message": "Report generated",
    "outputs": {
        "report_path": "./reports/...",
        "report_md": "./reports/..."
    },
    "intent": {...},               # Parsed intent
    "execution_time": 0.123,       # Seconds
    "timestamp": "2024-11-11T..."
}
```

#### `orchestrate_conversation(profile, max_turns=10)`

Orchestrate a multi-turn conversation maintaining context.

**Parameters:**
- `profile` (str): Profile to use for conversation
- `max_turns` (int): Maximum number of conversation turns

**Returns:** List of conversation turns with results

**Example:**
```python
from orchestrator import orchestrate_conversation

conversation = orchestrate_conversation("Sales", max_turns=5)
for turn in conversation:
    print(f"Turn {turn['turn']}: {turn['command']}")
    print(f"Result: {turn['result']['message']}")
```

#### `get_orchestration_history(limit=50)`

Get recent orchestration history.

**Parameters:**
- `limit` (int): Maximum number of history items to return

**Returns:** List of orchestration history items

**Example:**
```python
from orchestrator import get_orchestration_history

history = get_orchestration_history(limit=10)
for entry in history:
    print(f"{entry['timestamp']}: {entry['command']}")
    print(f"  Status: {entry['result']['status']}")
```

## Command Syntax

### Generate Report

```
generate report for <profile>
create report for <profile>
build report for <profile>
```

**Example:**
```python
execute_command("generate report for Sales")
```

### Summarize

```
summarize for <profile>
summary for <profile>
brief for <profile>
```

**Example:**
```python
execute_command("summarize for Marketing")
```

### Schedule

**Daily:**
```
schedule daily report for <profile> at <time>
```

**Example:**
```python
execute_command("schedule daily report for HR at 9:00")
```

**Interval:**
```
schedule report for <profile> every <N> minutes
```

**Example:**
```python
execute_command("schedule report for Sales every 30 minutes")
```

### Voice Output

```
speak for <profile>
say for <profile>
voice for <profile>
```

**Example:**
```python
execute_command("speak for Finance")
```

### List Operations

```
list profiles
show profiles
list reports
show reports
list schedules
show jobs
```

**Example:**
```python
execute_command("list profiles")
```

### Activate Profile

```
activate profile for <profile>
switch to <profile>
use <profile>
```

**Example:**
```python
execute_command("activate profile for Operations")
```

### Generate Chart

```
generate chart for <profile>
create trend chart for <profile>
make bar chart for <profile>
plot pie chart for <profile>
```

**Example:**
```python
execute_command("generate trend chart for Sales")
```

## Flask API Integration

### Execute Command Endpoint

```http
POST /api/command
Content-Type: application/json

{
  "command": "generate report for Sales",
  "profile": "Sales"  // optional, overrides parsed profile
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Report generated for Sales",
  "outputs": {
    "report_path": "./reports/sales_report.html"
  },
  "intent": {...},
  "execution_time": 0.234,
  "timestamp": "2024-11-11T13:45:00"
}
```

### Orchestration History Endpoint

```http
GET /api/orchestration/history?limit=20
```

**Response:**
```json
[
  {
    "command": "generate report for Sales",
    "intent": {...},
    "result": {...},
    "timestamp": "2024-11-11T13:45:00"
  }
]
```

### Dashboard Orchestration Endpoint

```http
GET /dashboard/orchestration
```

**Response:**
```json
{
  "success": true,
  "history": [...]
}
```

## Use Cases

### 1. Unified Command Interface

```python
from orchestrator import execute_command

# Single interface for all operations
execute_command("generate report for Sales")
execute_command("summarize for Marketing")
execute_command("schedule daily report for HR at 9:00")
execute_command("list profiles")
```

### 2. Voice-Activated Commands

```python
from voice_interface import record_and_transcribe
from orchestrator import execute_command

# Record voice command
command = record_and_transcribe(duration=5)

# Execute via orchestrator
result = execute_command(command)

# Speak result
from voice_interface import speak_text
speak_text(result["message"])
```

### 3. Automated Workflows

```python
from orchestrator import execute_command

# Morning briefing workflow
commands = [
    "activate profile for Sales",
    "summarize for Sales",
    "generate report for Sales",
    "speak for Sales"
]

for cmd in commands:
    result = execute_command(cmd)
    print(f"{cmd}: {result['status']}")
```

### 4. Dashboard Integration

```javascript
// Execute command from dashboard
fetch('/api/command', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        command: 'generate report for Sales'
    })
})
.then(response => response.json())
.then(data => {
    console.log(data.message);
});
```

### 5. Audit Trail

```python
from orchestrator import get_orchestration_history

# Get command history
history = get_orchestration_history(limit=100)

# Analyze usage patterns
actions = [h['intent']['action'] for h in history]
print(f"Most common action: {max(set(actions), key=actions.count)}")
```

## Logging

All orchestration activity is logged to `./reports/logs/orchestrator.log`:

```
2024-11-11 13:45:00 - INFO - Parsed intent: {'action': 'generate_report', 'profile': 'Sales', ...}
2024-11-11 13:45:01 - INFO - Command executed: generate_report - Status: success - Time: 0.23s
```

**Log Levels:**
- **INFO**: Normal operations (parsing, execution, completion)
- **WARNING**: Non-critical issues
- **ERROR**: Execution failures

## Error Handling

The orchestrator handles errors gracefully:

```python
result = execute_command("invalid command")

if result["status"] == "error":
    print(f"Error: {result['message']}")
    # Continue with fallback logic
```

**Common Errors:**
- Unknown action
- Missing profile
- Module not available
- Execution failure

## Performance

### Command Execution Times

- **Parse intent**: <1ms
- **List operations**: 1-10ms
- **Generate report**: 100-500ms
- **Schedule job**: 1-5ms
- **Voice output**: 500-2000ms

### History Storage

- In-memory storage (fast access)
- No size limit (grows with usage)
- Consider periodic cleanup for long-running systems

## Testing

Run the test suite:

```bash
python test_orchestrator.py
```

**Test Coverage:**
- ✓ Intent parsing (9 actions)
- ✓ Command execution
- ✓ Profile routing
- ✓ History tracking
- ✓ Error handling
- ✓ Offline operation

**Test Results:** 15/15 tests passing

## Extending the Orchestrator

### Adding New Commands

1. **Add intent parsing logic** in `parse_intent()`:

```python
elif any(word in text_lower for word in ["export", "download"]):
    intent["action"] = "export_data"
```

2. **Create handler function**:

```python
def _handle_export_data(intent: Dict[str, Any]) -> Dict[str, Any]:
    # Implementation
    return {
        "status": "success",
        "message": "Data exported",
        "outputs": {"file_path": "..."}
    }
```

3. **Add routing** in `execute_command()`:

```python
elif action == "export_data":
    result = _handle_export_data(intent)
```

### Custom Intent Parsers

Replace simple regex with ML-based parsing:

```python
def parse_intent_ml(text: str) -> Dict[str, Any]:
    # Use trained model for intent classification
    model = load_model("intent_classifier")
    intent = model.predict(text)
    return intent
```

## Best Practices

### Command Design

```python
# ✅ Good: Clear, specific commands
"generate report for Sales"
"schedule daily report for HR at 9:00"

# ❌ Bad: Ambiguous commands
"do something"
"make it work"
```

### Error Handling

```python
# ✅ Good: Check status and handle errors
result = execute_command(cmd)
if result["status"] == "success":
    process_outputs(result["outputs"])
else:
    log_error(result["message"])

# ❌ Bad: Assume success
result = execute_command(cmd)
process_outputs(result["outputs"])  # May fail
```

### Profile Management

```python
# ✅ Good: Explicit profile specification
execute_command("generate report for Sales")

# ✅ Also good: Use active profile
set_active_profile("Sales")
execute_command("generate report")  # Uses active profile
```

## Limitations

### Current

- Simple regex-based parsing (no ML)
- In-memory history (not persisted)
- No command queuing
- No parallel execution
- English language only

### Not Limitations

- ✅ Works completely offline
- ✅ No external dependencies
- ✅ Fast execution
- ✅ Extensible architecture

## Future Enhancements (Phase 4C+)

- ML-based intent classification
- Multi-language support
- Command queuing and prioritization
- Parallel command execution
- Persistent history storage
- Command templates
- Macro support
- Natural language generation for responses

## Examples

See `example_orchestrator.py` for complete examples including:
- Command execution
- Voice integration
- Dashboard integration
- Workflow automation

## License

Same as parent project.

## Support

For issues or questions, refer to the main project documentation.
