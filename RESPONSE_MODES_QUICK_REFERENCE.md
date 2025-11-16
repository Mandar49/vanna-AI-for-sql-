# Response Modes Quick Reference

## API Usage

### Query Parameter
```bash
# COMPACT mode
curl -X POST "http://localhost:5000/api/ask?mode=compact" \
  -H "Content-Type: application/json" \
  -d '{"question": "What were sales in 2024?", "conversation_id": "123"}'

# DETAILED mode (default)
curl -X POST "http://localhost:5000/api/ask?mode=detailed" \
  -H "Content-Type: application/json" \
  -d '{"question": "What were sales in 2024?", "conversation_id": "123"}'
```

### Request Body
```json
{
  "question": "What were sales in 2024?",
  "conversation_id": "123",
  "mode": "compact"
}
```

## Output Format

### COMPACT Mode
```
────────────────────────────────────────────────────────────
SQL RESULT
────────────────────────────────────────────────────────────
Year  TotalSales
2023  3770000.30
2024  5810000.45
────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────
ANALYST
────────────────────────────────────────────────────────────

Key Finding: Sales increased from 3770000.30 to 5810000.45
Observation: Growth of 54.1% year-over-year

Note: All numbers above are from the actual database query results.
```

### DETAILED Mode
```
────────────────────────────────────────────────────────────
SQL RESULT
────────────────────────────────────────────────────────────
Year  TotalSales
2023  3770000.30
2024  5810000.45
────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────
ANALYST
────────────────────────────────────────────────────────────

Key Finding: Sales increased from 3770000.30 in 2023 to 5810000.45 in 2024

Observations:
- 2023 sales: 3770000.30
- 2024 sales: 5810000.45
- Total growth: 2040000.15 (54.1% increase)

Data Summary: Two years of sales data showing consistent upward trend with strong year-over-year growth indicating positive business momentum.

Trend: Upward 📈 (+54.1% growth)

Note: All numbers above are from the actual database query results.
```

## Mode Characteristics

| Feature | COMPACT | DETAILED |
|---------|---------|----------|
| Length | ~300-500 chars | ~800-1200 chars |
| Data Rows | 5 max | 10-20 |
| Observations | 1-2 | 2-3+ |
| Recommendations | 1 | 2-3 |
| Trend Analysis | No | Yes |
| Scenarios | Base only | All (base, optimistic, pessimistic) |
| Use Case | Mobile, quick view | Desktop, full analysis |

## Programmatic Usage

```python
from response_composer import composer

# Set mode globally
composer.set_mode("COMPACT")

# Or pass mode to method
response = composer.compose_response(
    persona='analyst',
    query="What were sales?",
    analysis=analysis,
    raw_data=df.to_string(),
    df=df,
    mode="COMPACT"  # Override global setting
)
```

## Testing

```bash
# Run all tests including markdown verification
python test_sql_accuracy.py

# Run mode demo
python demo_response_modes.py
```

## No Markdown Guarantee

All responses are guaranteed to be plain text with:
- ❌ No bold (**text**)
- ❌ No italic (*text*)
- ❌ No headers (# text)
- ❌ No code blocks (```)
- ❌ No links ([text](url))
- ✅ Clean, structured plain text
- ✅ Separator lines (────)
- ✅ Clear section headers
- ✅ Emoji for trends (📈📉➖)

## When to Use Each Mode

### COMPACT
- Mobile applications
- Dashboard widgets
- Quick summaries
- Email notifications
- SMS/text messages
- Limited screen space

### DETAILED
- Desktop applications
- Full reports
- Executive briefings
- Comprehensive analysis
- Documentation
- Audit trails
