# Executive Intelligence Layer - Visualization Engine (Phase 2)

## Overview

The Visualization Engine (`viz.py`) provides offline matplotlib-based chart generation for executive reports. It integrates seamlessly with the Report Generator (Phase 1) to create complete, visually-rich business intelligence reports.

## Features

✅ **Three Chart Types**: Line charts, horizontal bar charts, and pie charts  
✅ **Fully Offline**: No internet, no remote fonts, no external APIs  
✅ **Auto-Organization**: Charts saved to `./reports/charts/`  
✅ **Clean Design**: Professional styling without custom themes  
✅ **Integration Ready**: Works seamlessly with `report_generator.py`  
✅ **Timestamp Naming**: Automatic unique filenames

## Installation

```bash
# Install required dependency
pip install matplotlib>=3.5.0
```

## Quick Start

```python
from viz import chart_sales_trend, chart_top_customers, chart_category_breakdown
import pandas as pd

# Sales trend line chart
df_trend = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar"],
    "Revenue": [100000, 120000, 135000]
})
path1 = chart_sales_trend(df_trend, "Month", "Revenue")

# Top customers bar chart
df_customers = pd.DataFrame({
    "Customer": ["Acme Corp", "TechStart", "Global Inc"],
    "Sales": [50000, 45000, 40000]
})
path2 = chart_top_customers(df_customers, "Customer", "Sales")

# Category pie chart
df_category = pd.DataFrame({
    "Product": ["Widget A", "Widget B", "Widget C"],
    "Revenue": [60000, 30000, 10000]
})
path3 = chart_category_breakdown(df_category, "Product", "Revenue")

print(f"Charts saved: {path1}, {path2}, {path3}")
```

## API Reference

### Core Functions

#### `ensure_chart_dir()`

Create the charts directory if it doesn't exist.

**Returns:** Absolute path to `./reports/charts/`

```python
from viz import ensure_chart_dir

chart_dir = ensure_chart_dir()
print(f"Charts will be saved to: {chart_dir}")
```

#### `chart_sales_trend(df, x_col, y_col, out_path=None)`

Generate a line chart showing trends over time.

**Parameters:**
- `df` (DataFrame): Data with time series
- `x_col` (str): Column name for x-axis (dates, periods, etc.)
- `y_col` (str): Column name for y-axis (values to plot)
- `out_path` (str, optional): Custom output path (auto-generated if None)

**Returns:** Absolute path to saved PNG file

**Example:**
```python
df = pd.DataFrame({
    "Quarter": ["Q1", "Q2", "Q3", "Q4"],
    "Revenue": [250000, 280000, 310000, 350000]
})

path = chart_sales_trend(df, "Quarter", "Revenue")
# Saves to: ./reports/charts/20241111_120000_sales_trend.png
```

**Chart Features:**
- Line with markers for data points
- Grid for readability
- Rotated x-axis labels (45°)
- Auto-scaled axes

#### `chart_top_customers(df, name_col, value_col, out_path=None, top_n=10)`

Generate a horizontal bar chart showing top performers.

**Parameters:**
- `df` (DataFrame): Data with names and values
- `name_col` (str): Column name for labels (customers, products, etc.)
- `value_col` (str): Column name for values
- `out_path` (str, optional): Custom output path
- `top_n` (int): Number of top items to display (default: 10)

**Returns:** Absolute path to saved PNG file

**Example:**
```python
df = pd.DataFrame({
    "Customer": ["Acme", "TechCo", "GlobalInc", "StartUp", "Enterprise"],
    "Revenue": [85000, 72000, 68000, 61000, 55000]
})

path = chart_top_customers(df, "Customer", "Revenue", top_n=5)
# Shows top 5 customers with value labels on bars
```

**Chart Features:**
- Horizontal bars (easier to read long names)
- Sorted by value (ascending for visual flow)
- Value labels on each bar
- Auto-limited to top N items

#### `chart_category_breakdown(df, name_col, value_col, out_path=None)`

Generate a pie chart showing percentage distribution.

**Parameters:**
- `df` (DataFrame): Data with categories and values
- `name_col` (str): Column name for category names
- `value_col` (str): Column name for values
- `out_path` (str, optional): Custom output path

**Returns:** Absolute path to saved PNG file

**Example:**
```python
df = pd.DataFrame({
    "Department": ["Engineering", "Sales", "Marketing", "Operations"],
    "Budget": [890000, 450000, 230000, 340000]
})

path = chart_category_breakdown(df, "Department", "Budget")
# Shows percentage breakdown with labels
```

**Chart Features:**
- Percentage labels on each slice
- Category names as labels
- Circular (equal aspect ratio)
- Auto-colored slices

## Integration with Report Generator

### Complete Workflow

```python
from viz import chart_sales_trend, chart_top_customers, chart_category_breakdown
from report_generator import build_executive_report
import pandas as pd

# 1. Prepare your data
df_results = pd.DataFrame({...})

# 2. Generate charts
charts = []
charts.append(chart_sales_trend(df_trend, "Month", "Sales"))
charts.append(chart_top_customers(df_customers, "Customer", "Revenue"))
charts.append(chart_category_breakdown(df_categories, "Product", "Sales"))

# 3. Generate report with embedded charts
report = build_executive_report(
    title="Q4 Business Review",
    question="How did we perform in Q4?",
    sql="SELECT ...",
    df=df_results,
    insights="Strong growth observed...",
    charts=charts  # Pass chart paths here!
)

print(f"Report with charts: {report['paths']['html_path']}")
```

### Chart Embedding

Charts are embedded in reports as Markdown image links:

```markdown
## Visualizations

**Chart 1:**

![Chart 1](./reports/charts/20241111_120000_sales_trend.png)

**Chart 2:**

![Chart 2](./reports/charts/20241111_120000_top_customers.png)
```

In HTML reports, these render as `<img>` tags with proper styling.

## File Naming Convention

Charts are automatically named using timestamps:

```
./reports/charts/<timestamp>_<chart_type>.png
```

Examples:
- `20241111_120000_sales_trend.png`
- `20241111_120001_top_customers.png`
- `20241111_120002_category_breakdown.png`

This ensures:
- Unique filenames (no overwrites)
- Chronological ordering
- Easy identification

## Chart Specifications

### Sales Trend Chart
- **Type:** Line chart
- **Size:** 10" × 6"
- **DPI:** 100
- **Format:** PNG
- **Features:** Markers, grid, rotated labels

### Top Customers Chart
- **Type:** Horizontal bar chart
- **Size:** 10" × 6"
- **DPI:** 100
- **Format:** PNG
- **Features:** Value labels, sorted, top N only

### Category Breakdown Chart
- **Type:** Pie chart
- **Size:** 10" × 8"
- **DPI:** 100
- **Format:** PNG
- **Features:** Percentage labels, circular

## Customization

### Custom Output Path

```python
# Save to specific location
custom_path = "./my_charts/custom_name.png"
chart_sales_trend(df, "X", "Y", out_path=custom_path)
```

### Limiting Top Items

```python
# Show only top 5 instead of default 10
chart_top_customers(df, "Name", "Value", top_n=5)
```

## Testing

Run the test suite:

```bash
# Run all tests
python test_viz.py

# Or with pytest
pytest test_viz.py -v
```

Tests verify:
- ✓ Chart directory creation
- ✓ All three chart types
- ✓ Auto path generation
- ✓ File existence and validity
- ✓ Offline operation
- ✓ Edge case handling

## Troubleshooting

### Matplotlib Not Found

```bash
pip install matplotlib
```

### Charts Not Displaying in Report

Ensure chart paths are passed to `build_executive_report()`:

```python
charts = [path1, path2, path3]  # List of paths
report = build_executive_report(..., charts=charts)
```

### Charts Directory Not Created

The directory is created automatically. If you see errors, check write permissions.

### Backend Errors

The code uses `Agg` backend (non-interactive) for offline use. This is set automatically:

```python
import matplotlib
matplotlib.use('Agg')
```

## Performance

- **Small datasets** (<100 rows): <0.1 seconds per chart
- **Medium datasets** (100-1000 rows): 0.1-0.3 seconds per chart
- **Large datasets** (>1000 rows): 0.3-1 second per chart

Charts are limited to reasonable sizes:
- Top customers: Default top 10 (configurable)
- Pie charts: All categories (consider limiting to <10 for readability)

## Best Practices

### Data Preparation

```python
# Sort data before charting
df_sorted = df.sort_values('Revenue', ascending=False)
chart_top_customers(df_sorted, 'Customer', 'Revenue', top_n=10)

# Aggregate small categories
df['Category'] = df['Category'].apply(
    lambda x: 'Other' if x in small_categories else x
)
```

### Chart Selection

- **Line charts**: Time series, trends, sequential data
- **Bar charts**: Rankings, comparisons, top performers
- **Pie charts**: Proportions, percentages, composition (max 7-8 categories)

### Integration Tips

```python
# Generate charts conditionally
charts = []
if has_time_series:
    charts.append(chart_sales_trend(df_trend, 'Date', 'Sales'))
if has_rankings:
    charts.append(chart_top_customers(df_top, 'Name', 'Value'))
if has_categories:
    charts.append(chart_category_breakdown(df_cat, 'Category', 'Amount'))

# Pass to report generator
report = build_executive_report(..., charts=charts)
```

## Limitations

- Fixed chart types (3 types available)
- No interactive features (static PNG images)
- No custom color schemes (uses matplotlib defaults)
- No animation or real-time updates
- Maximum recommended categories for pie charts: 8

## Future Enhancements (Phase 3+)

- Additional chart types (scatter, heatmap, stacked bar)
- Custom color palettes
- Interactive charts (Plotly integration)
- Chart templates
- Automatic chart type selection
- Multi-chart dashboards

## Examples

See `example_viz_integration.py` for complete examples including:
- Individual chart generation
- Integration with report generator
- End-to-end workflow
- Multiple chart types in one report

## License

Same as parent project.

## Support

For issues or questions, refer to the main project documentation.
