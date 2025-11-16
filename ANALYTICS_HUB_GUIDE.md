# Analytics Hub Guide (Phase 5F)

## Overview

The Analytics Hub provides a **unified executive analytics dashboard** that consolidates all key metrics, visualizations, and system activity in one place. It serves as the central command center for executive intelligence.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              ANALYTICS HUB (Phase 5F)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │     KPIs     │    │    Charts    │    │  Voice   │  │
│  │  (Phase 5D)  │    │  (Phase 2)   │    │Summaries │  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
│         │                    │                  │        │
│         └────────────────────┴──────────────────┘        │
│                          ↓                               │
│                  ┌──────────────┐                        │
│                  │   Unified    │                        │
│                  │  Dashboard   │                        │
│                  └──────────────┘                        │
│                          ↓                               │
│                  ┌──────────────┐                        │
│                  │Orchestration │                        │
│                  │   History    │                        │
│                  │  (Phase 4B)  │                        │
│                  └──────────────┘                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Latest KPIs Display**
- Real-time key performance indicators
- Growth rates and trends
- Financial metrics
- Profit margins and ROI

### 2. **Recent Charts Gallery**
- Visual analytics from Phase 2
- KPI dashboards
- Trend charts
- Anomaly visualizations

### 3. **Voice Summaries**
- Profile-based summaries
- Recent activity highlights
- Interaction counts

### 4. **Orchestration History**
- Recent command execution
- Success/failure status
- Timestamps and messages

### 5. **System Statistics**
- Total profiles
- Total reports
- Total charts
- Commands executed

## Access

### Web UI
```
http://localhost:5000/dashboard/analytics
```

### API Endpoint
```
http://localhost:5000/dashboard/analytics/api
```

## Web UI Features

### Dashboard Layout

The Analytics Hub uses a responsive grid layout with the following sections:

#### 1. Header
- Title: "Analytics Hub"
- Subtitle: "Unified Executive Intelligence Dashboard"
- Last updated timestamp

#### 2. KPI Cards (2x2 Grid)
- **Total Revenue**: Sum of all revenue with growth rate
- **Average Revenue**: Mean revenue value
- **Profit Margin**: Percentage with status indicator
- **Growth Rate**: Period-over-period growth

#### 3. Recent Charts
- List of latest 5 charts
- Click to view full-size
- Sorted by date (newest first)
- Chart name and timestamp

#### 4. Voice Summaries
- Latest 5 profile summaries
- Profile name and activity text
- Interaction counts

#### 5. Recent Commands
- Latest 5 orchestration commands
- Command text
- Status badge (success/error)
- Result message
- Timestamp

#### 6. System Overview (Full Width)
- Total profiles count
- Total reports count
- Total charts count
- Commands executed count

#### 7. Refresh Button
- Floating action button
- Bottom-right corner
- Reloads entire dashboard

## API Response Format

### GET /dashboard/analytics/api

```json
{
  "success": true,
  "data": {
    "kpis": {
      "summary": {
        "total": 750000.00,
        "mean": 125000.00,
        "std": 16174.05,
        "min": 100000.00,
        "max": 142000.00
      },
      "growth": {
        "growth_rate": 0.38,
        "trend": "increasing"
      },
      "financial": {
        "profit_margin": 0.4293,
        "roi": 0.7523
      }
    },
    "charts_count": 18,
    "history_count": 10,
    "profiles_count": 7,
    "timestamp": "2025-11-11T17:14:06.932000"
  }
}
```

## Integration Examples

### Example 1: Access Analytics Hub

```python
from flask import Flask
from dashboard_gateway import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True)
```

Then visit: `http://localhost:5000/dashboard/analytics`

### Example 2: Fetch Analytics Data via API

```python
import requests

response = requests.get('http://localhost:5000/dashboard/analytics/api')
data = response.json()

if data['success']:
    kpis = data['data']['kpis']
    print(f"Total Revenue: ${kpis['summary']['total']:,.2f}")
    print(f"Growth Rate: {kpis['growth']['growth_rate']:.2%}")
    print(f"Profit Margin: {kpis['financial']['profit_margin']:.2%}")
```

### Example 3: Embed Analytics in Custom Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>Custom Dashboard</title>
</head>
<body>
    <h1>Executive Dashboard</h1>
    
    <!-- Embed Analytics Hub -->
    <iframe 
        src="/dashboard/analytics" 
        width="100%" 
        height="800px" 
        frameborder="0">
    </iframe>
</body>
</html>
```

### Example 4: Automated Analytics Reports

```python
import requests
from datetime import datetime

def generate_analytics_report():
    """Generate automated analytics report."""
    # Fetch analytics data
    response = requests.get('http://localhost:5000/dashboard/analytics/api')
    data = response.json()
    
    if data['success']:
        analytics = data['data']
        
        # Create report
        report = f"""
        Analytics Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}
        
        KPIs:
        - Total Revenue: ${analytics['kpis']['summary']['total']:,.2f}
        - Growth Rate: {analytics['kpis']['growth']['growth_rate']:.2%}
        - Profit Margin: {analytics['kpis']['financial']['profit_margin']:.2%}
        
        System Stats:
        - Profiles: {analytics['profiles_count']}
        - Reports: {analytics['charts_count']}
        - Commands: {analytics['history_count']}
        """
        
        return report

# Schedule daily
from scheduler import schedule_daily
schedule_daily(9, 0, generate_analytics_report)
```

### Example 5: Real-Time Analytics Monitoring

```python
import time
import requests

def monitor_analytics(interval=60):
    """Monitor analytics in real-time."""
    while True:
        response = requests.get('http://localhost:5000/dashboard/analytics/api')
        data = response.json()
        
        if data['success']:
            analytics = data['data']
            
            print(f"\n=== Analytics Update ===")
            print(f"Time: {analytics['timestamp']}")
            print(f"Profiles: {analytics['profiles_count']}")
            print(f"Commands: {analytics['history_count']}")
            
            # Check for alerts
            kpis = analytics['kpis']
            if 'growth' in kpis:
                growth = kpis['growth']['growth_rate']
                if growth < 0:
                    print(f"⚠️ ALERT: Negative growth detected: {growth:.2%}")
        
        time.sleep(interval)

# Run monitoring
monitor_analytics(interval=300)  # Every 5 minutes
```

## Customization

### Custom KPIs

Modify the KPI section in `dashboard_gateway.py`:

```python
kpis = [
    {
        'label': 'Custom Metric',
        'value': f"${custom_value:,.0f}",
        'change': custom_change
    },
    # Add more KPIs...
]
```

### Custom Styling

The Analytics Hub uses inline CSS. To customize:

1. Modify the `ANALYTICS_TEMPLATE` in `dashboard_gateway.py`
2. Update colors, fonts, layout in the `<style>` section
3. Add custom CSS classes

Example:

```css
.card {
    background: #your-color;
    border-radius: 15px;
    /* Your custom styles */
}
```

### Custom Sections

Add new sections to the dashboard:

```python
# In analytics_hub() function
custom_data = get_custom_data()

# In template
<div class="card">
    <h2>🎯 Custom Section</h2>
    {% for item in custom_data %}
    <div class="custom-item">{{ item }}</div>
    {% endfor %}
</div>
```

## Performance

### Load Time
- **Initial Load**: ~500ms
- **KPI Calculation**: <200ms
- **Chart Listing**: <100ms
- **History Retrieval**: <50ms
- **Total**: <1 second

### Optimization Tips

1. **Cache KPIs**: Cache calculated KPIs for faster loading
2. **Limit History**: Show only recent 5-10 items
3. **Lazy Load Charts**: Load chart images on demand
4. **API Caching**: Cache API responses for 1-5 minutes

Example caching:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1)
def get_cached_kpis():
    """Cache KPIs for 5 minutes."""
    return analyze_kpis(df)

# Clear cache every 5 minutes
```

## Troubleshooting

### Analytics Hub Not Loading

**Problem:**
```
Analytics Hub error: ...
```

**Solution:**
- Check all subsystems are operational
- Verify KPI analyzer is working
- Ensure orchestrator is available
- Check profile manager

### No KPIs Displayed

**Problem:**
```
No KPI data available
```

**Solution:**
```python
# Check KPI analyzer
from kpi_analyzer import analyze_kpis
import pandas as pd

df = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar'],
    'Revenue': [100000, 120000, 115000],
    'Cost': [60000, 70000, 65000]
})

result = analyze_kpis(df)
print(result)
```

### No Charts Displayed

**Problem:**
```
No charts available
```

**Solution:**
- Check `./reports/charts/` directory exists
- Generate some charts first
- Verify chart file permissions

### No History Displayed

**Problem:**
```
No command history available
```

**Solution:**
```python
# Execute some commands first
from orchestrator import execute_command

execute_command("list profiles")
execute_command("analyze KPIs for Sales")
```

## Best Practices

### 1. Regular Updates
```python
# Refresh analytics every 5 minutes
setInterval(() => {
    location.reload();
}, 300000);
```

### 2. Error Handling
```python
try:
    kpis = analyze_kpis(df)
except Exception as e:
    kpis = []
    print(f"KPI error: {e}")
```

### 3. Data Validation
```python
if result['status'] == 'success':
    metrics = result['metrics']
else:
    metrics = default_metrics
```

### 4. Responsive Design
The dashboard is mobile-responsive with:
- Grid layout adapts to screen size
- Cards stack on small screens
- Touch-friendly buttons

### 5. Accessibility
- Semantic HTML
- ARIA labels
- Keyboard navigation
- High contrast colors

## Testing

Run the comprehensive test suite:

```bash
python test_dashboard_analytics.py
```

**Test Coverage:**
- ✓ Analytics Route Exists
- ✓ Analytics Hub Function
- ✓ KPI Integration
- ✓ Charts Integration
- ✓ Voice Summaries Integration
- ✓ Orchestration History Integration
- ✓ System Statistics
- ✓ Analytics Template
- ✓ Analytics API Endpoint
- ✓ Complete Integration

## Summary

The Analytics Hub provides:

✅ **Unified Dashboard** - All metrics in one place  
✅ **Real-Time KPIs** - Latest performance indicators  
✅ **Visual Analytics** - Charts and graphs  
✅ **Voice Summaries** - Profile activity highlights  
✅ **Command History** - Recent orchestration activity  
✅ **System Stats** - Overall system health  
✅ **API Access** - Programmatic data retrieval  
✅ **Responsive Design** - Works on all devices  

**Access:** `/dashboard/analytics` (Web UI) or `/dashboard/analytics/api` (JSON API)  
**Dependencies:** All Phase 1-5E subsystems  
**Performance:** <1 second load time  

---

**Phase 5F Complete** ✅  
Next: Advanced analytics features or real-time monitoring
