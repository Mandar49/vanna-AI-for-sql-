"""
Export Manager - Handle CSV and PDF exports of query results
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
import os

class ExportManager:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        Path(export_dir).mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(self, question: str = None, sql: str = None, df: pd.DataFrame = None, 
                     summary: str = None, use_last_result: bool = False) -> dict:
        """
        Export query results to CSV
        
        Args:
            question: User's question
            sql: SQL query executed
            df: DataFrame with results
            summary: Analysis summary (optional)
            use_last_result: Use saved last query result if df is None
        
        Returns:
            dict with success status and file path
        """
        try:
            # Check if we should use last saved result
            if df is None or use_last_result:
                result = self._load_last_query_result()
                if not result['success']:
                    return result
                df = result['df']
                sql = result['sql']
                question = question or "Last Query"
            
            if df is None or df.empty:
                return {
                    'success': False,
                    'message': 'No data available for export. Please run a query first.'
                }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.csv"
            filepath = os.path.join(self.export_dir, filename)
            
            # Create metadata header
            metadata = [
                f"# Question: {question or 'Query'}",
                f"# SQL: {sql or 'N/A'}",
                f"# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"# Rows: {len(df)}",
                ""
            ]
            
            if summary:
                metadata.insert(3, f"# Summary: {summary}")
            
            # Write metadata and data
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(metadata) + '\n')
                df.to_csv(f, index=False)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'message': f'Exported to {filename}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'CSV export failed: {str(e)}'
            }
    
    def _load_last_query_result(self) -> dict:
        """Load last saved query result"""
        try:
            import json
            from pathlib import Path
            
            temp_dir = Path("temp")
            csv_path = temp_dir / "last_query_result.csv"
            metadata_path = temp_dir / "last_query_metadata.json"
            
            if not csv_path.exists():
                return {
                    'success': False,
                    'message': 'No data available for export. Please run a query first.'
                }
            
            df = pd.read_csv(csv_path)
            
            sql = "N/A"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    sql = metadata.get('sql', 'N/A')
            
            return {
                'success': True,
                'df': df,
                'sql': sql
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Failed to load last query result: {str(e)}'
            }
    
    def export_to_pdf(self, question: str, sql: str, df: pd.DataFrame, 
                     summary: str = None, dark_mode: bool = False, use_last_result: bool = False) -> dict:
        """
        Export query results to PDF
        
        Args:
            question: User's question
            sql: SQL query executed
            df: DataFrame with results
            summary: Analysis summary (optional)
            dark_mode: Use dark theme for PDF
            use_last_result: Use saved last query result if df is None
        
        Returns:
            dict with success status and file path
        """
        try:
            # Check if we should use last saved result
            if df is None or use_last_result:
                result = self._load_last_query_result()
                if not result['success']:
                    return result
                df = result['df']
                sql = result['sql']
                question = question or "Last Query"
            
            if df is None or df.empty:
                return {
                    'success': False,
                    'message': 'No data available for export. Please run a query first.'
                }
            
            # Try to import WeasyPrint, auto-install if missing
            try:
                from weasyprint import HTML, CSS
            except ImportError:
                print("[INFO] WeasyPrint not found. Attempting auto-installation...")
                install_result = self._auto_install_weasyprint()
                
                if not install_result['success']:
                    return {
                        'success': False,
                        'message': install_result['message']
                    }
                
                # Try importing again after installation
                try:
                    from weasyprint import HTML, CSS
                    print("[OK] WeasyPrint installed and imported successfully")
                except ImportError as e:
                    return {
                        'success': False,
                        'message': f'WeasyPrint installation succeeded but import failed: {str(e)}. Please restart the application.'
                    }
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.pdf"
            filepath = os.path.join(self.export_dir, filename)
            
            # Generate HTML content
            html_content = self._generate_pdf_html(
                question, sql, df, summary, dark_mode
            )
            
            # Convert HTML to PDF
            HTML(string=html_content).write_pdf(filepath)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'message': f'Exported to {filename}'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'PDF export failed: {str(e)}'
            }
    
    def _auto_install_weasyprint(self) -> dict:
        """
        Attempt to automatically install WeasyPrint
        
        Returns:
            dict with success status and message
        """
        try:
            import subprocess
            import sys
            
            print("[INFO] Installing WeasyPrint...")
            
            # Run pip install
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'weasyprint'],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                print("[OK] WeasyPrint installed successfully")
                return {
                    'success': True,
                    'message': 'WeasyPrint installed successfully'
                }
            else:
                error_msg = result.stderr or result.stdout
                print(f"[ERROR] WeasyPrint installation failed: {error_msg}")
                return {
                    'success': False,
                    'message': f'WeasyPrint auto-installation failed. Please install manually: pip install weasyprint'
                }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': 'WeasyPrint installation timed out. Please install manually: pip install weasyprint'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'WeasyPrint auto-installation error: {str(e)}. Please install manually: pip install weasyprint'
            }
    
    def _generate_pdf_html(self, question: str, sql: str, df: pd.DataFrame, 
                          summary: str = None, dark_mode: bool = False) -> str:
        """Generate HTML content for PDF export"""
        
        # Color scheme
        if dark_mode:
            bg_color = '#1E1E1E'
            text_color = '#E5E5E5'
            card_bg = '#2D2D2D'
            border_color = '#3D3D3D'
            accent_color = '#00BFA6'
            code_bg = '#000000'
        else:
            bg_color = '#FFFFFF'
            text_color = '#2c3e50'
            card_bg = '#F8F9FA'
            border_color = '#E0E0E0'
            accent_color = '#667eea'
            code_bg = '#2D2D2D'
        
        # Format timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Convert DataFrame to HTML table
        table_html = df.to_html(index=False, classes='data-table', border=0)
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Query Export - {timestamp}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: {bg_color};
            color: {text_color};
            line-height: 1.6;
            margin: 0;
            padding: 20px;
        }}
        
        .header {{
            border-bottom: 3px solid {accent_color};
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: {accent_color};
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        
        .timestamp {{
            color: {text_color};
            opacity: 0.7;
            font-size: 14px;
        }}
        
        .section {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            page-break-inside: avoid;
        }}
        
        .section h2 {{
            color: {accent_color};
            margin: 0 0 15px 0;
            font-size: 20px;
            border-bottom: 2px solid {border_color};
            padding-bottom: 10px;
        }}
        
        .question {{
            font-size: 16px;
            font-weight: 500;
            color: {text_color};
            margin-bottom: 10px;
        }}
        
        .sql-code {{
            background-color: {code_bg};
            color: #F8F8F2;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 10px;
        }}
        
        .data-table th {{
            background-color: {accent_color};
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 8px 10px;
            border-bottom: 1px solid {border_color};
        }}
        
        .data-table tr:nth-child(even) {{
            background-color: {card_bg};
        }}
        
        .summary {{
            background-color: {card_bg};
            border-left: 4px solid {accent_color};
            padding: 15px;
            margin-top: 10px;
            font-size: 14px;
            line-height: 1.8;
        }}
        
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid {border_color};
            text-align: center;
            font-size: 12px;
            opacity: 0.7;
        }}
        
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: {accent_color};
        }}
        
        .stat-label {{
            font-size: 12px;
            opacity: 0.7;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Query Export Report</h1>
        <div class="timestamp">Generated: {timestamp}</div>
    </div>
    
    <div class="section">
        <h2>Question</h2>
        <div class="question">{question}</div>
    </div>
    
    <div class="section">
        <h2>SQL Query</h2>
        <div class="sql-code">{sql}</div>
    </div>
    
    <div class="section">
        <h2>Results</h2>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{len(df)}</div>
                <div class="stat-label">Rows</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(df.columns)}</div>
                <div class="stat-label">Columns</div>
            </div>
        </div>
        {table_html}
    </div>
"""
        
        if summary:
            html += f"""
    <div class="section">
        <h2>Summary</h2>
        <div class="summary">{summary}</div>
    </div>
"""
        
        html += f"""
    <div class="footer">
        AI Business Intelligence Agent | Exported on {timestamp}
    </div>
</body>
</html>
"""
        
        return html

# Global export manager instance
export_manager = ExportManager()
