# Dashboard Validation Panel - Quick Reference

## Access Dashboard
```
http://localhost:5000/dashboard
```

## UI Elements

### Toggle Button
**Location:** Top-right corner
**Label:** 📊 Data Validation
**Action:** Opens/closes validation panel

### Validation Panel
**Location:** Right side (slides in)
**Width:** 400px
**Sections:**
1. Active Database
2. Tables Loaded
3. Last SQL Executed
4. Execution Time
5. Refresh Schema Button

## API Endpoints

### GET /dashboard/validation_data
Retrieve current database validation information

**Response:**
```json
{
    "database": "ad_ai_testdb",
    "table_count": 5,
    "last_sql": "SELECT * FROM salesorders...",
    "execution_time": "0.023s"
}
```

### POST /dashboard/refresh_schema
Refresh database schema

**Response (Success):**
```json
{
    "success": true,
    "message": "Schema refreshed successfully. Found 5 tables.",
    "table_count": 5,
    "tables": ["salesorders", "customers", ...]
}
```

**Response (Error):**
```json
{
    "success": false,
    "message": "Failed to refresh schema: ..."
}
```

### POST /api/refresh_schema
Alternative refresh endpoint in main app

**Same response format as dashboard endpoint**

## JavaScript Functions

### Toggle Panel
```javascript
toggleValidationPanel()
```

### Show Toast
```javascript
showToast('Message here', false)  // Success (green)
showToast('Error message', true)  // Error (red)
```

### Load Data
```javascript
loadValidationData()
```

### Refresh Schema
```javascript
refreshSchema()
```

## CSS Classes

### Panel
```css
.validation-panel       /* Main panel */
.validation-panel.open  /* Open state */
```

### Content
```css
.validation-header      /* Header section */
.validation-content     /* Content area */
.validation-item        /* Data item */
.validation-label       /* Item label */
.validation-value       /* Item value */
.validation-value.code  /* Code block */
```

### Buttons
```css
.refresh-btn            /* Refresh button */
.toggle-panel-btn       /* Toggle button */
.close-panel            /* Close button */
```

### Toast
```css
.toast                  /* Toast notification */
.toast.show             /* Visible state */
.toast.error            /* Error state */
```

## Color Reference

| Element | Color | Hex |
|---------|-------|-----|
| Header | Purple | #667eea |
| Refresh Button | Green | #2ecc71 |
| Success Toast | Green | #2ecc71 |
| Error Toast | Red | #e74c3c |
| Background | White | #FFFFFF |

## Database Config

```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ad_ai_testdb'
}
```

## Testing Commands

### Test Validation Data
```bash
curl http://localhost:5000/dashboard/validation_data
```

### Test Schema Refresh
```bash
curl -X POST http://localhost:5000/dashboard/refresh_schema
```

### Test Alternative Endpoint
```bash
curl -X POST http://localhost:5000/api/refresh_schema
```

## Common Tasks

### Open Panel
1. Click "📊 Data Validation" button
2. Panel slides in from right

### Refresh Schema
1. Open validation panel
2. Click "🔄 Refresh Schema"
3. Wait for success toast

### Close Panel
1. Click × in panel header
2. Or click toggle button again

### View Last SQL
- Scroll in "Last SQL Executed" section
- Full query visible in code block

## Troubleshooting

### Panel Won't Open
- Check JavaScript console for errors
- Verify `toggleValidationPanel()` function exists
- Check if panel element exists in DOM

### Data Not Loading
- Check `/dashboard/validation_data` endpoint
- Verify database connection
- Check browser console for fetch errors

### Refresh Fails
- Verify database is running
- Check database credentials
- Review error toast message
- Check server logs

### Toast Not Showing
- Verify `showToast()` function exists
- Check toast element in DOM
- Verify CSS classes applied

## Browser Compatibility

- Chrome/Edge: ✓ Full support
- Firefox: ✓ Full support
- Safari: ✓ Full support
- Mobile: ✓ Responsive overlay

## Keyboard Shortcuts

Currently none implemented. Future enhancement:
- `Ctrl+D` - Toggle panel
- `Ctrl+R` - Refresh schema
- `Esc` - Close panel
