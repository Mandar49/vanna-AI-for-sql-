# Phase 1 SQL Core Fixes - Quick Reference

## Key Files

| File | Purpose |
|------|---------|
| `schema_manager.py` | Schema caching and validation |
| `sql_corrector.py` | SQL execution with retry |
| `export_manager.py` | Export with saved results |
| `test_phase1_sql_fixes.py` | Test suite |

## Directory Structure

```
cache/schema_cache.json          # Schema cache
logs/query_rewrites.log          # Rewrite log
temp/last_query_result.csv       # Last result
temp/last_query_metadata.json    # Metadata
exports/export_*.csv             # Exports
```

## Common Operations

### Refresh Schema Cache
```python
from schema_manager import schema_manager
schema_manager.refresh_schema_cache()
```

### Execute Query with Retry
```python
from sql_corrector import corrector
result = corrector.execute_with_retry(sql, max_retries=3)
```

### Export Last Result
```python
from export_manager import export_manager
result = export_manager.export_to_csv(use_last_result=True)
```

### Validate Query
```python
from schema_manager import schema_manager
is_valid, missing, corrected = schema_manager.validate_query(sql)
```

## Table Fallbacks

| Wrong Name | Corrects To |
|------------|-------------|
| sales_2024 | salesorders |
| orders_2024 | salesorders |
| order_items | orderitems |
| customer_list | customers |
| product_list | products |

## Error Codes

| Code | Error | Handling |
|------|-------|----------|
| 1064 | Syntax Error | No retry, return error |
| 1146 | Table Not Found | Return fallback message |
| 2003 | Connection Refused | Retry 3x with 1s delay |
| 2006 | Server Gone Away | Retry 3x with 1s delay |
| 2013 | Lost Connection | Retry 3x with 1s delay |

## Testing

```bash
# Run all tests
python test_phase1_sql_fixes.py

# Test specific query
python -c "from sql_corrector import corrector; print(corrector.execute_with_retry('SELECT * FROM salesorders LIMIT 5'))"
```

## API Endpoints

### Export Report
```bash
POST /api/export_report
{
  "format": "csv",
  "question": "Query",
  "sql": "SELECT...",
  "results": [],  # Optional - uses last result if empty
  "summary": "Summary",
  "dark_mode": false
}
```

### Refresh Schema
```bash
POST /api/refresh_schema
```

## Troubleshooting

### Schema Not Loading
```bash
# Check cache
cat cache/schema_cache.json

# Force refresh
python -c "from schema_manager import schema_manager; schema_manager.refresh_schema_cache()"
```

### Export Fails
```bash
# Check temp files
ls -la temp/
cat temp/last_query_result.csv
```

### Query Fails
```bash
# Check logs
cat logs/query_rewrites.log
cat logs/errors.log
```

## Performance

- Schema cache: 24 hour TTL
- Query validation: < 10ms
- Connection retry: 3 attempts, 1s delay
- Auto-save: Automatic on success

## Key Features

✓ Automatic table name correction
✓ Connection retry (3 attempts)
✓ Schema validation
✓ Auto-save results
✓ Export from cache
✓ Comprehensive logging
✓ Graceful error handling
