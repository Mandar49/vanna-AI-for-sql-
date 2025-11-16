# Export Feature - Quick Reference

## User Interface

### Export Button Location
- Appears next to "Show SQL" button
- Only visible for messages with SQL queries
- Label: "📥 Export ▼"

### Export Options
1. **📄 CSV** - Comma-separated values
2. **📕 PDF** - Portable document format

## API Endpoint

### POST /api/export_report

**Request:**
```json
{
    "format": "csv",
    "question": "What were sales in 2024?",
    "sql": "SELECT * FROM salesorders...",
    "results": [{"Year": 2024, "Sales": 4110315.23}],
    "summary": "Total sales were...",
    "dark_mode": false
}
```

**Response:**
- Success: File download
- Error: JSON with error message

## Export Formats

### CSV
```csv
# Question: What were sales in 2024?
# SQL: SELECT * FROM salesorders...
# Timestamp: 2024-11-12 15:30:45
# Rows: 1247

Year,TotalSales
2024,4110315.23
```

### PDF
- Professional report layout
- Theme support (light/dark)
- Syntax-highlighted SQL
- Styled data tables
- Print-ready format

## File Naming

**Format:** `export_YYYYMMDD_HHMMSS.{format}`

**Examples:**
- `export_20241112_153045.csv`
- `export_20241112_153045.pdf`

## Theme Support

### Light Mode
- Background: #FFFFFF
- Text: #2c3e50
- Accent: #667eea

### Dark Mode
- Background: #1E1E1E
- Text: #E5E5E5
- Accent: #00BFA6

**Auto-detected from UI theme**

## JavaScript Functions

### Export Message
```javascript
exportMessage(message, format)
```

### Show Toast
```javascript
showExportToast(message, type)
// Types: 'success', 'error', 'info'
```

## Installation

```bash
pip install weasyprint
```

## Testing

### Test CSV
```bash
curl -X POST http://localhost:5000/api/export_report \
  -H "Content-Type: application/json" \
  -d '{"format":"csv","question":"Test","sql":"SELECT 1","results":[{"col":"val"}]}' \
  --output test.csv
```

### Test PDF
```bash
curl -X POST http://localhost:5000/api/export_report \
  -H "Content-Type: application/json" \
  -d '{"format":"pdf","question":"Test","sql":"SELECT 1","results":[{"col":"val"}],"dark_mode":false}' \
  --output test.pdf
```

## Common Issues

### WeasyPrint Not Installed
```
Error: WeasyPrint not installed
Solution: pip install weasyprint
```

### No Results to Export
```
Error: No results to export
Solution: Ensure results array is not empty
```

### Unsupported Format
```
Error: Unsupported format: xml
Solution: Use 'csv' or 'pdf'
```

## Browser Support

- Chrome: ✓
- Firefox: ✓
- Safari: ✓
- Edge: ✓
- Mobile: ✓

## Performance

| Format | Speed | Size | Best For |
|--------|-------|------|----------|
| CSV | Fast | Small | Large datasets |
| PDF | Moderate | Medium | Reports, sharing |

## Export Contents

All exports include:
1. Question asked
2. SQL query used
3. Results table
4. Summary text
5. Timestamp

## Usage Flow

1. Ask question → Get results
2. Click "Export" button
3. Select CSV or PDF
4. File downloads automatically
5. Success toast appears
