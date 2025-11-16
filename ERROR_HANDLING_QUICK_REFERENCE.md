# Error Handling Quick Reference

## Error Types & Messages

### 1. Empty Result
**Trigger:** Query executes successfully but returns no data

**User Message:**
```
────────────────────────────────────────────────────────────
NO DATA FOUND
────────────────────────────────────────────────────────────

No data found for this query.

Possible causes:
- No data exists for the given year or time period
- Filters are too narrow or restrictive
- The database tables may need to be populated

Suggestion: Try 'Show me all customers' or 'List all orders' to verify data exists.
```

**Logged As:** `EMPTY_RESULT`

### 2. Syntax Error
**Trigger:** MySQL error 1064 or "syntax" in error message

**User Message:**
```
────────────────────────────────────────────────────────────
SQL ERROR
────────────────────────────────────────────────────────────

Invalid SQL syntax. Please adjust your query or check table names.

Suggestion: Try rephrasing your question or ask 'What tables are available?'
```

**Logged As:** `SYNTAX_ERROR`

### 3. Table Not Found
**Trigger:** MySQL error 1146 or "doesn't exist" in error message

**User Message:**
```
────────────────────────────────────────────────────────────
SQL ERROR
────────────────────────────────────────────────────────────

Table or column not found. Please check the database schema.

Suggestion: Try rephrasing your question or ask 'What tables are available?'
```

**Logged As:** `TABLE_NOT_FOUND`

### 4. Column Not Found
**Trigger:** MySQL error 1054 or "unknown column" in error message

**User Message:**
```
────────────────────────────────────────────────────────────
SQL ERROR
────────────────────────────────────────────────────────────

Column not found. Please verify column names in the database.

Suggestion: Try rephrasing your question or ask 'What tables are available?'
```

**Logged As:** `COLUMN_NOT_FOUND`

### 5. Generic Execution Error
**Trigger:** Any other SQL execution failure

**User Message:**
```
────────────────────────────────────────────────────────────
SQL ERROR
────────────────────────────────────────────────────────────

SQL execution failed. Please try rephrasing your question.

Suggestion: Try rephrasing your question or ask 'What tables are available?'
```

**Logged As:** `EXECUTION_ERROR`

## Programmatic Usage

### Log an Error
```python
from error_logger import error_logger

error_logger.log_sql_error(
    error_type="SYNTAX_ERROR",
    sql="SELECT * FROM invalid_table",
    error_message="Table 'invalid_table' doesn't exist",
    question="Show me all data",
    context={"mode": "DETAILED", "user": "analyst"}
)
```

### Retrieve Recent Errors
```python
from error_logger import error_logger

# Get last 10 errors
recent = error_logger.get_recent_errors(n=10)

for error in recent:
    print(error)
```

### Clear Error Log
```python
from error_logger import error_logger

error_logger.clear_log()
```

## API Endpoints

### GET /api/error_logs
Retrieve recent error logs

**Request:**
```bash
curl "http://localhost:5000/api/error_logs?n=10"
```

**Response:**
```json
{
  "errors": [
    "[2024-11-12 14:30:45] SQL ERROR: SYNTAX_ERROR\nQuestion: What were sales?\n...",
    "[2024-11-12 14:31:20] SQL ERROR: EMPTY_RESULT\nQuestion: Show 2099 data\n..."
  ],
  "count": 2
}
```

### DELETE /api/error_logs
Clear all error logs

**Request:**
```bash
curl -X DELETE "http://localhost:5000/api/error_logs"
```

**Response:**
```json
{
  "success": true,
  "message": "Error logs cleared"
}
```

## Log File Format

**Location:** `logs/errors.log`

**Format:**
```
======================================================================
[2024-11-12 14:30:45] SQL ERROR: SYNTAX_ERROR
======================================================================
Question: What were sales in 2024?

SQL Query:
SELECT COUNT(*) FROM salesorders WHERE YEAR = 2024

Error Message:
You have an error in your SQL syntax near 'YEAR = 2024'

Context:
  mode: DETAILED
  profile: analyst_profile
  correction_applied: False
======================================================================
```

## Mode Differences

### COMPACT Mode
- Shows only user-friendly message
- No technical details
- Brief suggestion

### DETAILED Mode
- Shows user-friendly message
- Includes technical error details
- Shows SQL query
- Shows correction attempts (if any)
- Full suggestion text

## Testing

### Run All Tests
```bash
python test_sql_accuracy.py
```

### Run Demo
```bash
python demo_error_handling.py
```

### Specific Tests
- **TEST 10:** Empty result handling
- **TEST 11:** Syntax error handling
- **TEST 12:** Error log retrieval
- **TEST 13:** Plain text format verification

## Common Scenarios

### Scenario 1: User asks for data that doesn't exist
```
User: "What were sales in 2099?"
System: NO DATA FOUND message
Log: EMPTY_RESULT error logged
```

### Scenario 2: User's question generates bad SQL
```
User: "Show me sales where year is 2024"
System: SQL ERROR message (syntax)
Log: SYNTAX_ERROR error logged
```

### Scenario 3: User references non-existent table
```
User: "Show me data from products table"
System: SQL ERROR message (table not found)
Log: TABLE_NOT_FOUND error logged
```

## Best Practices

1. **Always log errors** - Use error_logger for all SQL failures
2. **Provide context** - Include question, mode, profile in logs
3. **User-friendly messages** - Never show raw MySQL errors to users
4. **Plain text format** - Consistent with response format
5. **Mode-aware** - Show appropriate detail level
6. **Actionable suggestions** - Tell users what to try next

## Troubleshooting

### Error log not created?
- Check if `logs/` directory exists
- Verify write permissions
- Check error_logger initialization

### Errors not appearing in log?
- Verify error_logger.log_sql_error() is called
- Check if log was recently cleared
- Verify file path is correct

### Can't retrieve errors?
- Check if log file exists
- Verify file is not corrupted
- Try clearing and recreating log
