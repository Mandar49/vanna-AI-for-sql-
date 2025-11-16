# Executive Intelligence Layer - Report Generator (Phase 1)

## Overview

The Report Generator converts SQL query results and analysis insights into professional executive-style reports. It operates **fully offline** with no external API dependencies.

## Features

✅ **Multi-format Output**: Generates Markdown, HTML, and optionally PDF reports  
✅ **Fully Offline**: No cloud services or external APIs required  
✅ **Executive-Ready**: Professional formatting with clear sections  
✅ **Auto-Organization**: Reports saved to `./reports/` directory  
✅ **Data Visualization**: Supports embedding chart images  
✅ **Graceful Degradation**: PDF generation optional (works without dependencies)

## Installation

```bash
# Install required dependencies
pip install pandas markdown

# Optional: For PDF generation
pip install weasyprint
# OR
pip install reportlab
```

## Quick Start

```python
from report_generator import build_executive_report
import pandas as pd

# Your query results
df = pd.DataFrame({
    "Product": ["Widget A", "Widget B"],
    "Sales": [1000, 1500]
})

# Generate report
result = build_executive_report(
    title="Q4 Sales Analysis",
    question="What are the top-selling products?",
    sql="SELECT product, SUM(sales) FROM sales GROUP BY product",
    df=df,
    insights="Widget B leads with 1500 units sold.",
    charts=None  # Optional: list of chart file paths
)

print(f"Report saved to: {result['paths']['md_path']}")
```

## API Reference

### Core Functions

#### `build_executive_report()`

Main function to generate a complete executive report.

**Parameters:**
- `title` (str): Report title
- `question` (str): Business question being answered
- `sql` (str): SQL query used
- `df` (DataFrame): Query results
- `insights` (str): Analysis insights/summary
- `charts` (list[str], optional): List of chart image paths

**Returns:**
```python
{
    "title": "Report Title",
    "basename": "report_title_20241111_120000",
    "paths": {
        "md_path": "./reports/report.md",
        "html_path": "./reports/report.html",
        "pdf_path": "./reports/report.pdf"  # or None
    },
    "timestamp": "2024-11-11T12:00:00"
}
```

#### `tabulate_df(df, max_rows=50)`

Convert DataFrame to Markdown table.

**Parameters:**
- `df` (DataFrame): Data to convert
- `max_rows` (int): Maximum rows to display (default: 50)

**Returns:** Markdown table string

#### `render_markdown(title, sections)`

Compose Markdown document from sections.

**Parameters:**
- `title` (str): Document title
- `sections` (list[tuple]): List of (section_title, section_content) tuples

**Returns:** Complete Markdown document string

#### `save_report(markdown_str, basename)`

Save report in multiple formats.

**Parameters:**
- `markdown_str` (str): Markdown content
- `basename` (str): Base filename (without extension)

**Returns:** Dict with file paths

## Report Structure

Generated reports include these sections:

1. **Executive Summary** - Key insights and findings
2. **Question Asked** - Original business question
3. **SQL Query** - Query used (syntax highlighted)
4. **Data Preview** - First 50 rows in table format
5. **Visualizations** - Embedded charts (if provided)
6. **Recommendations** - Next steps and action items

## Integration with Existing System

### With Business Analyst

```python
from business_analyst import BusinessAnalyst
from report_generator import build_executive_report

# After getting insights from business analyst
analyst = BusinessAnalyst()
insights = analyst.analyze(question, sql, df)

# Generate report
report = build_executive_report(
    title="Business Analysis Report",
    question=question,
    sql=sql,
    df=df,
    insights=insights
)
```

### With Flask App

```python
from flask import jsonify
from report_generator import build_executive_report

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    
    result = build_executive_report(
        title=data['title'],
        question=data['question'],
        sql=data['sql'],
        df=pd.DataFrame(data['results']),
        insights=data['insights']
    )
    
    return jsonify({
        "success": True,
        "report_url": result['paths']['html_path']
    })
```

## Output Examples

### Markdown Output
```markdown
# Q4 Sales Analysis

**Generated:** 2024-11-11 12:00:00

---

## Executive Summary

Widget B leads with 1500 units sold...

## Data Preview

| Product | Sales |
| --- | --- |
| Widget A | 1000 |
| Widget B | 1500 |
```

### HTML Output
Professional styled HTML with:
- Responsive design
- Syntax-highlighted SQL
- Formatted tables with hover effects
- Clean typography

### PDF Output (Optional)
Print-ready PDF with same styling as HTML.

## Configuration

### Reports Directory

By default, reports are saved to `./reports/`. This directory is created automatically.

### File Naming

Reports are named using the pattern:
```
<title_lowercase>_<timestamp>.{md,html,pdf}
```

Example: `q4_sales_analysis_20241111_120000.md`

## Testing

Run the test suite:

```bash
# Run all tests
python test_report_generator.py

# Or with pytest
pytest test_report_generator.py -v
```

Tests verify:
- ✓ Directory creation
- ✓ DataFrame to Markdown conversion
- ✓ Report file generation
- ✓ Offline operation
- ✓ Graceful PDF fallback

## Troubleshooting

### PDF Generation Not Working

PDF generation is optional. If you see "PDF skipped", install dependencies:

```bash
# Option 1: WeasyPrint (recommended)
pip install weasyprint

# Option 2: ReportLab (fallback)
pip install reportlab
```

### Markdown Tables Not Rendering in HTML

Ensure the `markdown` library is installed:

```bash
pip install markdown
```

### Reports Directory Not Created

The directory is created automatically. If you see permission errors, check write permissions in your working directory.

## Performance

- **Small datasets** (<1000 rows): <1 second
- **Medium datasets** (1000-10000 rows): 1-3 seconds
- **Large datasets** (>10000 rows): Only first 50 rows shown in report

## Limitations

- Maximum 50 rows displayed in data preview (configurable)
- PDF generation requires external dependencies
- Chart embedding requires pre-generated image files
- No real-time data refresh (static reports)

## Future Enhancements (Phase 2+)

- Interactive HTML reports with JavaScript
- Chart generation integration
- Email delivery
- Scheduled report generation
- Template customization
- Multi-language support

## License

Same as parent project.

## Support

For issues or questions, refer to the main project documentation or create an issue in the repository.
