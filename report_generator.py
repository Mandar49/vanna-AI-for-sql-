"""
Executive Intelligence Layer - Report Generator (Phase 1)
Converts SQL + analysis results into executive-style reports.
Fully offline, no external APIs.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import pandas as pd


def ensure_dir(path: str) -> None:
    """Create directories if they don't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def tabulate_df(df: pd.DataFrame, max_rows: int = 50) -> str:
    """
    Return a Markdown-formatted pipe table (no external deps).
    
    Args:
        df: DataFrame to convert
        max_rows: Maximum number of rows to include
        
    Returns:
        Markdown table string
    """
    if df is None or df.empty:
        return "_No data available_"
    
    # Limit rows
    display_df = df.head(max_rows)
    
    # Build header
    headers = list(display_df.columns)
    header_row = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    
    # Build data rows
    data_rows = []
    for _, row in display_df.iterrows():
        row_str = "| " + " | ".join(str(v) if pd.notna(v) else "" for v in row) + " |"
        data_rows.append(row_str)
    
    table = "\n".join([header_row, separator] + data_rows)
    
    if len(df) > max_rows:
        table += f"\n\n_Showing {max_rows} of {len(df)} rows_"
    
    return table


def render_markdown(title: str, sections: List[Tuple[str, str]]) -> str:
    """
    Compose a Markdown string from title and sections.
    
    Args:
        title: Report title
        sections: List of (section_title, section_content) tuples
        
    Returns:
        Complete Markdown document
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_parts = [
        f"# {title}",
        "",
        f"**Generated:** {timestamp}",
        "",
        "---",
        ""
    ]
    
    for section_title, section_content in sections:
        md_parts.extend([
            f"## {section_title}",
            "",
            section_content,
            "",
            "---",
            ""
        ])
    
    return "\n".join(md_parts)


def markdown_to_html(markdown_str: str) -> str:
    """
    Convert Markdown to HTML using built-in approach or markdown library.
    
    Args:
        markdown_str: Markdown content
        
    Returns:
        HTML string
    """
    try:
        import markdown
        html_body = markdown.markdown(markdown_str, extensions=['tables', 'fenced_code'])
    except ImportError:
        # Fallback: basic conversion without markdown library
        html_body = markdown_str.replace("\n", "<br>\n")
        html_body = html_body.replace("# ", "<h1>").replace("\n", "</h1>\n", 1)
        html_body = html_body.replace("## ", "<h2>").replace("\n", "</h2>\n")
    
    # Wrap in full HTML document
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    return html


def save_report(markdown_str: str, basename: str) -> Dict[str, Optional[str]]:
    """
    Save report files under ./reports/ directory.
    
    Args:
        markdown_str: Markdown content
        basename: Base filename (without extension)
        
    Returns:
        Dict with paths: {"md_path", "html_path", "pdf_path"}
    """
    reports_dir = "./reports"
    ensure_dir(reports_dir)
    
    result = {
        "md_path": None,
        "html_path": None,
        "pdf_path": None
    }
    
    # Save Markdown
    md_path = os.path.join(reports_dir, f"{basename}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_str)
    result["md_path"] = md_path
    
    # Save HTML
    html_content = markdown_to_html(markdown_str)
    html_path = os.path.join(reports_dir, f"{basename}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    result["html_path"] = html_path
    
    # Try to save PDF (optional)
    pdf_path = os.path.join(reports_dir, f"{basename}.pdf")
    try:
        # Try weasyprint first
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(pdf_path)
        result["pdf_path"] = pdf_path
    except ImportError:
        try:
            # Try reportlab as fallback
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Simple text conversion
            for line in markdown_str.split("\n"):
                if line.strip():
                    story.append(Paragraph(line, styles['Normal']))
                    story.append(Spacer(1, 12))
            
            doc.build(story)
            result["pdf_path"] = pdf_path
        except Exception:
            # PDF generation not available, skip gracefully
            pass
    
    return result


def build_executive_report(
    title: str,
    question: str,
    sql: str,
    df: pd.DataFrame,
    insights: str,
    charts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Build a complete executive report from analysis components.
    
    Args:
        title: Report title
        question: Business question asked
        sql: SQL query used
        df: Result DataFrame
        insights: Analysis insights/summary
        charts: List of chart file paths (optional)
        
    Returns:
        Dict with report paths and metadata
    """
    sections = []
    
    # Executive Summary
    sections.append(("Executive Summary", insights))
    
    # Question Asked
    sections.append(("Question Asked", f"**Business Question:**\n\n{question}"))
    
    # SQL Used
    sql_section = f"```sql\n{sql}\n```"
    sections.append(("SQL Query", sql_section))
    
    # Data Preview
    if df is not None and not df.empty:
        data_preview = tabulate_df(df, max_rows=50)
        sections.append(("Data Preview", data_preview))
    else:
        sections.append(("Data Preview", "_No data returned_"))
    
    # Charts
    if charts:
        chart_section = []
        for i, chart_path in enumerate(charts, 1):
            chart_section.append(f"**Chart {i}:**\n\n![Chart {i}]({chart_path})")
        sections.append(("Visualizations", "\n\n".join(chart_section)))
    
    # Recommendations
    recommendations = """
**Next Steps:**

1. Review the data patterns identified in the analysis
2. Validate findings with domain experts
3. Consider additional drill-down queries for deeper insights
4. Monitor key metrics over time for trend analysis
5. Share findings with relevant stakeholders
"""
    sections.append(("Recommendations", recommendations))
    
    # Render markdown
    markdown_content = render_markdown(title, sections)
    
    # Generate basename from title
    basename = title.lower().replace(" ", "_").replace("/", "_")
    basename = f"{basename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Save report
    paths = save_report(markdown_content, basename)
    
    return {
        "title": title,
        "basename": basename,
        "paths": paths,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Quick test
    print("Testing Report Generator...")
    
    # Create sample data
    sample_df = pd.DataFrame({
        "Product": ["Widget A", "Widget B", "Widget C"],
        "Sales": [1000, 1500, 800],
        "Region": ["North", "South", "East"]
    })
    
    result = build_executive_report(
        title="Q4 Sales Analysis",
        question="What are the top-selling products by region?",
        sql="SELECT product, SUM(sales) as total_sales, region FROM sales GROUP BY product, region",
        df=sample_df,
        insights="Widget B leads in sales with 1500 units in the South region. North and East regions show moderate performance.",
        charts=None
    )
    
    print(f"✅ Report generated:")
    print(f"   MD: {result['paths']['md_path']}")
    print(f"   HTML: {result['paths']['html_path']}")
    print(f"   PDF: {result['paths']['pdf_path'] or 'Skipped (dependencies not available)'}")
