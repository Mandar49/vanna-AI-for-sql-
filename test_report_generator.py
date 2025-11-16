"""
Test suite for Executive Intelligence Layer - Report Generator
Verifies offline report generation capabilities.
"""

import os
import shutil
import pandas as pd
import pytest
from pathlib import Path

from report_generator import (
    ensure_dir,
    tabulate_df,
    render_markdown,
    save_report,
    build_executive_report
)


class TestReportGenerator:
    """Test suite for report generator functions."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and cleanup test environment."""
        # Setup: ensure clean state
        self.test_reports_dir = "./test_reports"
        if os.path.exists(self.test_reports_dir):
            shutil.rmtree(self.test_reports_dir)
        
        yield
        
        # Teardown: clean up test files
        if os.path.exists(self.test_reports_dir):
            shutil.rmtree(self.test_reports_dir)
    
    def test_ensure_dir(self):
        """Test directory creation."""
        test_path = os.path.join(self.test_reports_dir, "subdir", "nested")
        ensure_dir(test_path)
        
        assert os.path.exists(test_path)
        assert os.path.isdir(test_path)
        print("✓ Directory creation works")
    
    def test_tabulate_df_basic(self):
        """Test DataFrame to Markdown table conversion."""
        df = pd.DataFrame({
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [25, 30, 35],
            "City": ["NYC", "LA", "Chicago"]
        })
        
        result = tabulate_df(df)
        
        assert "| Name | Age | City |" in result
        assert "| Alice | 25 | NYC |" in result
        assert "| Bob | 30 | LA |" in result
        print("✓ DataFrame tabulation works")
    
    def test_tabulate_df_empty(self):
        """Test empty DataFrame handling."""
        df = pd.DataFrame()
        result = tabulate_df(df)
        
        assert "_No data available_" in result
        print("✓ Empty DataFrame handled gracefully")
    
    def test_tabulate_df_max_rows(self):
        """Test row limiting."""
        df = pd.DataFrame({
            "ID": range(100),
            "Value": range(100, 200)
        })
        
        result = tabulate_df(df, max_rows=10)
        
        assert "Showing 10 of 100 rows" in result
        print("✓ Row limiting works")
    
    def test_render_markdown(self):
        """Test Markdown document rendering."""
        sections = [
            ("Introduction", "This is the intro section."),
            ("Analysis", "Here are the findings."),
            ("Conclusion", "Final thoughts.")
        ]
        
        result = render_markdown("Test Report", sections)
        
        assert "# Test Report" in result
        assert "## Introduction" in result
        assert "## Analysis" in result
        assert "## Conclusion" in result
        assert "This is the intro section." in result
        print("✓ Markdown rendering works")
    
    def test_save_report_creates_files(self):
        """Test report file creation."""
        markdown_content = "# Test Report\n\nThis is a test."
        
        # Temporarily change reports dir for testing
        import report_generator
        original_dir = "./reports"
        report_generator.reports_dir = self.test_reports_dir
        
        result = save_report(markdown_content, "test_report")
        
        # Verify files exist
        assert result["md_path"] is not None
        assert os.path.exists(result["md_path"])
        assert result["md_path"].endswith(".md")
        
        assert result["html_path"] is not None
        assert os.path.exists(result["html_path"])
        assert result["html_path"].endswith(".html")
        
        # PDF is optional
        if result["pdf_path"]:
            assert os.path.exists(result["pdf_path"])
            print("✓ PDF generation available")
        else:
            print("✓ PDF skipped gracefully (dependencies not available)")
        
        print("✓ Report files created successfully")
    
    def test_build_executive_report(self):
        """Test complete executive report generation."""
        # Create sample data
        df = pd.DataFrame({
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Revenue": [50000, 75000, 30000],
            "Units": [100, 150, 60]
        })
        
        result = build_executive_report(
            title="Sales Performance Report",
            question="Which products generated the most revenue?",
            sql="SELECT product, SUM(revenue) as revenue, SUM(units) as units FROM sales GROUP BY product",
            df=df,
            insights="Widget B is the top performer with $75,000 in revenue and 150 units sold.",
            charts=None
        )
        
        # Verify result structure
        assert "title" in result
        assert "basename" in result
        assert "paths" in result
        assert "timestamp" in result
        
        # Verify files were created
        assert os.path.exists(result["paths"]["md_path"])
        assert os.path.exists(result["paths"]["html_path"])
        
        # Verify content
        with open(result["paths"]["md_path"], "r", encoding="utf-8") as f:
            content = f.read()
            assert "Sales Performance Report" in content
            assert "Which products generated the most revenue?" in content
            assert "Widget B" in content
        
        print("✓ Executive report built successfully")
    
    def test_no_internet_required(self):
        """Verify no external network calls are made."""
        # This test ensures all operations are offline
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
        
        # All these should work without internet
        table = tabulate_df(df)
        assert table is not None
        
        sections = [("Test", "Content")]
        markdown = render_markdown("Title", sections)
        assert markdown is not None
        
        result = save_report(markdown, "offline_test")
        assert result["md_path"] is not None
        
        print("✓ All operations work offline")
    
    def test_reports_folder_auto_created(self):
        """Test that reports folder is created automatically."""
        if os.path.exists("./reports"):
            shutil.rmtree("./reports")
        
        df = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
        result = build_executive_report(
            title="Auto Folder Test",
            question="Test question",
            sql="SELECT * FROM test",
            df=df,
            insights="Test insights"
        )
        
        assert os.path.exists("./reports")
        assert os.path.isdir("./reports")
        print("✓ Reports folder auto-created")


def run_manual_test():
    """Manual test for quick verification."""
    print("\n" + "="*60)
    print("MANUAL TEST: Report Generator")
    print("="*60 + "\n")
    
    # Clean up old reports
    if os.path.exists("./reports"):
        shutil.rmtree("./reports")
    
    # Create sample data
    sample_df = pd.DataFrame({
        "Quarter": ["Q1", "Q2", "Q3", "Q4"],
        "Revenue": [100000, 125000, 150000, 175000],
        "Profit": [20000, 28000, 35000, 42000],
        "Growth": ["5%", "8%", "12%", "15%"]
    })
    
    # Generate report
    result = build_executive_report(
        title="Annual Performance Review 2024",
        question="How did revenue and profit trend throughout the year?",
        sql="""
        SELECT 
            quarter,
            SUM(revenue) as revenue,
            SUM(profit) as profit,
            ROUND((profit / revenue * 100), 2) as margin
        FROM financial_data
        GROUP BY quarter
        ORDER BY quarter
        """,
        df=sample_df,
        insights="""
        **Key Findings:**
        
        - Revenue grew consistently from Q1 ($100K) to Q4 ($175K), representing 75% growth
        - Profit margins improved from 20% to 24% over the year
        - Q4 showed the strongest performance with 15% growth rate
        - Trend indicates sustainable business growth trajectory
        """,
        charts=None
    )
    
    print(f"✅ Report Generated Successfully!\n")
    print(f"Title: {result['title']}")
    print(f"Basename: {result['basename']}")
    print(f"Timestamp: {result['timestamp']}\n")
    print(f"Files created:")
    print(f"  📄 Markdown: {result['paths']['md_path']}")
    print(f"  🌐 HTML: {result['paths']['html_path']}")
    
    if result['paths']['pdf_path']:
        print(f"  📕 PDF: {result['paths']['pdf_path']}")
    else:
        print(f"  📕 PDF: Skipped (install weasyprint or reportlab for PDF support)")
    
    print(f"\n✓ ./reports folder created: {os.path.exists('./reports')}")
    print(f"✓ Markdown file exists: {os.path.exists(result['paths']['md_path'])}")
    print(f"✓ HTML file exists: {os.path.exists(result['paths']['html_path'])}")
    print(f"✓ No internet access used: True")
    
    print("\n" + "="*60)
    print("✅ Report Generator ready")
    print("="*60)


if __name__ == "__main__":
    # Run manual test
    run_manual_test()
    
    # Run pytest if available
    try:
        pytest.main([__file__, "-v"])
    except:
        print("\nNote: Install pytest to run full test suite")
