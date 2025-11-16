# Phase 3 UI Polish - Quick Reference

## Card Colors (Dark Mode)

| Card Type | Background | Use |
|-----------|------------|-----|
| data | #1E1E1E | SQL results |
| insight | #181818 | AI analysis |
| strategist | #1A1D2E | Strategic notes |
| error | #251313 | Errors |

## Animation Timing

```css
.output-card {
    animation: fadeIn 0.15s ease-in;
    transition: all 0.15s ease;
}
```

## Query Cache

### Add to Cache
```python
from query_cache import query_cache

query_cache.add_query(
    question="What were sales?",
    sql="SELECT...",
    result_summary="100 rows, 3 columns",
    row_count=100
)
```

### Get Recent Queries
```python
recent = query_cache.get_recent_queries(n=5)
```

### Clear Cache
```python
query_cache.clear_cache()
```

### Cache Stats
```python
stats = query_cache.get_cache_stats()
```

## API Endpoints

### Clear Cache
```bash
POST /api/clear_cache
```

Response:
```json
{
  "success": true,
  "message": "Query cache cleared"
}
```

## UI Elements

### Clear Cache Button
```html
<button onclick="clearQueryCache()">
    Clear Cache
</button>
```

### Theme Toggle
Already implemented with localStorage persistence.

## Smooth Scrolling

```css
html {
    scroll-behavior: smooth;
}
```

## Cache File Location

```
cache/query_history.json
```

## Performance

- Animation: 150ms (down from 300ms)
- Cache: Last 5 queries
- Scroll: Smooth native
- Hover: 150ms transition

## Testing

```bash
# Test query
Ask: "Which product generated highest profit margin in 2024?"

# Expected
✓ Smooth fade-in (150ms)
✓ Proper card colors
✓ Export works
✓ Cache updated
```

## Troubleshooting

### Check Cache
```bash
cat cache/query_history.json
```

### Verify Colors
```javascript
// Check dark mode
document.documentElement.classList.contains('dark')
```

### Test Clear Cache
```javascript
clearQueryCache()
```

## Key Files

- `query_cache.py` - Cache management
- `templates/index.html` - UI enhancements
- `static/script.js` - Clear cache function
- `ad_ai_app.py` - Clear cache endpoint
- `sql_corrector.py` - Cache integration
