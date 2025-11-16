"""
Output Formatter - Clean card-based output rendering
Removes markdown, creates styled sections, and provides consistent formatting
"""
import re
from typing import Dict, List, Optional

class OutputFormatter:
    def __init__(self):
        self.card_types = {
            'data': {
                'bg_light': '#F8F9FA',
                'bg_dark': '#2D2D2D',
                'border_light': '#E0E0E0',
                'border_dark': '#3D3D3D',
                'title': 'Data Result'
            },
            'insight': {
                'bg_light': '#F5F7FA',
                'bg_dark': '#181818',
                'border_light': '#D0D5DD',
                'border_dark': '#2D2D2D',
                'title': 'Insight'
            },
            'strategist': {
                'bg_light': '#F0F4FF',
                'bg_dark': '#1A1D2E',
                'border_light': '#C7D2FE',
                'border_dark': '#2E3A59',
                'title': 'Strategist Note'
            },
            'error': {
                'bg_light': '#FEF2F2',
                'bg_dark': '#251313',
                'border_light': '#FCA5A5',
                'border_dark': '#7F1D1D',
                'title': 'Error'
            },
            'sql': {
                'bg_light': '#F9FAFB',
                'bg_dark': '#1E1E1E',
                'border_light': '#D1D5DB',
                'border_dark': '#374151',
                'title': 'SQL Query Used'
            }
        }
    
    def strip_markdown(self, text: str) -> str:
        """
        Remove all markdown formatting from text
        
        Args:
            text: Text with markdown
        
        Returns:
            Plain text without markdown
        """
        if not text:
            return text
        
        # Remove bold/italic markers
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'\1', text)  # Bold+italic
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)          # Italic
        text = re.sub(r'__(.+?)__', r'\1', text)          # Bold (underscore)
        text = re.sub(r'_(.+?)_', r'\1', text)            # Italic (underscore)
        
        # Remove headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove code blocks markers (keep content)
        text = re.sub(r'```[\w]*\n', '', text)
        text = re.sub(r'```', '', text)
        text = re.sub(r'`(.+?)`', r'\1', text)
        
        # Remove links but keep text
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
        
        # Remove horizontal rules
        text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
        
        # Clean up emoji-only markdown
        text = re.sub(r'^\s*[📊📈📉🧭✍️💬]\s*\*\*(.+?)\*\*:', r'\1:', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def render_card(self, section: str, content: str, card_type: str = 'data', 
                   collapsible: bool = False) -> str:
        """
        Render content as a styled card
        
        Args:
            section: Section title
            content: Content to display
            card_type: Type of card (data, insight, strategist, error, sql)
            collapsible: Whether the card should be collapsible
        
        Returns:
            HTML string for the card
        """
        card_config = self.card_types.get(card_type, self.card_types['data'])
        
        # Strip markdown from content
        clean_content = self.strip_markdown(content)
        
        # Generate unique ID for collapsible
        card_id = "card_" + str(hash(section + content) % 10000)
        
        # Build collapse button if needed
        collapse_button = ""
        if collapsible:
            collapse_button = '<button class="collapse-btn" onclick="toggleCard(\'' + card_id + '\')">▼</button>'
        
        # Build display style for collapsible content
        display_style = ' style="display:none;"' if collapsible else ''
        
        # Format content
        formatted_content = self._format_content(clean_content, card_type)
        
        # Build card HTML using concatenation
        card_html = (
            '<div class="output-card output-card-' + card_type + '" data-card-type="' + card_type + '">\n'
            '    <div class="output-card-header">\n'
            '        <h3 class="output-card-title">' + section + '</h3>\n'
            '        ' + collapse_button + '\n'
            '    </div>\n'
            '    <div class="output-card-content" id="' + card_id + '"' + display_style + '>\n'
            '        ' + formatted_content + '\n'
            '    </div>\n'
            '</div>\n'
        )
        
        return card_html
    
    def _format_content(self, content: str, card_type: str) -> str:
        """Format content based on card type"""
        if card_type == 'sql':
            # SQL code formatting
            return f'<pre class="sql-code">{content}</pre>'
        elif card_type == 'data':
            # Check if content looks like a table
            if '\n' in content and ('|' in content or '\t' in content):
                return self._format_table(content)
            else:
                return f'<div class="data-content">{content}</div>'
        else:
            # Regular text content
            lines = content.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a list item
                if line.startswith('- ') or line.startswith('• '):
                    formatted_lines.append(f'<li>{line[2:]}</li>')
                elif line.endswith(':') and len(line) < 50:
                    # Likely a heading
                    formatted_lines.append(f'<div class="content-heading">{line}</div>')
                else:
                    formatted_lines.append(f'<p>{line}</p>')
            
            # Wrap list items in ul
            html = '\n'.join(formatted_lines)
            html = re.sub(r'(<li>.*?</li>\s*)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
            
            return html
    
    def _format_table(self, content: str) -> str:
        """Format table-like content"""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not lines:
            return content
        
        # Simple table formatting
        table_html = '<table class="data-table">'
        
        # First line as header
        if lines:
            headers = re.split(r'\s{2,}|\t', lines[0])
            table_html += '<thead><tr>'
            for header in headers:
                table_html += f'<th>{header}</th>'
            table_html += '</tr></thead>'
        
        # Rest as data rows
        if len(lines) > 1:
            table_html += '<tbody>'
            for line in lines[1:]:
                if not line or line.startswith('-'):
                    continue
                cells = re.split(r'\s{2,}|\t', line)
                table_html += '<tr>'
                for cell in cells:
                    table_html += f'<td>{cell}</td>'
                table_html += '</tr>'
            table_html += '</tbody>'
        
        table_html += '</table>'
        return table_html
    
    def format_response(self, response_data: Dict) -> str:
        """
        Format complete response with multiple sections
        
        Args:
            response_data: Dictionary with sections
                {
                    'data': 'DataFrame content',
                    'insight': 'Analysis text',
                    'sql': 'SQL query',
                    'error': 'Error message'
                }
        
        Returns:
            Complete HTML with all cards
        """
        html_parts = []
        
        # Order: Data → Insight → SQL → Error
        section_order = [
            ('data', 'Data Result', 'data', False),
            ('insight', 'Insight', 'insight', False),
            ('strategist', 'Strategist Note', 'strategist', False),
            ('sql', 'SQL Query Used', 'sql', True),
            ('error', 'Error', 'error', False)
        ]
        
        for key, title, card_type, collapsible in section_order:
            if key in response_data and response_data[key]:
                html_parts.append(
                    self.render_card(title, response_data[key], card_type, collapsible)
                )
        
        return '\n'.join(html_parts)
    
    def get_card_styles(self) -> str:
        """Get CSS styles for cards"""
        return '''
<style>
.output-card {
    background: var(--card-bg, #F8F9FA);
    border: 1px solid var(--card-border, #E0E0E0);
    border-radius: 8px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.output-card-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--card-border, #E0E0E0);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--card-header-bg, rgba(0, 0, 0, 0.02));
}

.output-card-title {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary, #2c3e50);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.output-card-content {
    padding: 16px;
    color: var(--text-secondary, #4a5568);
    line-height: 1.6;
}

.collapse-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 12px;
    color: var(--text-secondary, #6b7280);
    transition: transform 0.2s;
}

.collapse-btn:hover {
    color: var(--text-primary, #2c3e50);
}

.collapse-btn.collapsed {
    transform: rotate(-90deg);
}

/* Card type specific styles */
.output-card-data {
    --card-bg: #F8F9FA;
    --card-border: #E0E0E0;
}

.dark .output-card-data {
    --card-bg: #2D2D2D;
    --card-border: #3D3D3D;
}

.output-card-insight {
    --card-bg: #F5F7FA;
    --card-border: #D0D5DD;
}

.dark .output-card-insight {
    --card-bg: #181818;
    --card-border: #2D2D2D;
}

.output-card-strategist {
    --card-bg: #F0F4FF;
    --card-border: #C7D2FE;
}

.dark .output-card-strategist {
    --card-bg: #1A1D2E;
    --card-border: #2E3A59;
}

.output-card-error {
    --card-bg: #FEF2F2;
    --card-border: #FCA5A5;
}

.dark .output-card-error {
    --card-bg: #251313;
    --card-border: #7F1D1D;
}

.output-card-sql {
    --card-bg: #F9FAFB;
    --card-border: #D1D5DB;
}

.dark .output-card-sql {
    --card-bg: #1E1E1E;
    --card-border: #374151;
}

/* Content formatting */
.sql-code {
    background: #2D2D2D;
    color: #F8F8F2;
    padding: 12px;
    border-radius: 4px;
    overflow-x: auto;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    margin: 0;
}

.dark .sql-code {
    background: #000000;
}

.data-content {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    white-space: pre-wrap;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.data-table th {
    background: var(--accent, #00BFA6);
    color: white;
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
}

.data-table td {
    padding: 8px 12px;
    border-bottom: 1px solid var(--card-border, #E0E0E0);
}

.data-table tr:nth-child(even) {
    background: rgba(0, 0, 0, 0.02);
}

.dark .data-table tr:nth-child(even) {
    background: rgba(255, 255, 255, 0.02);
}

.content-heading {
    font-weight: 600;
    margin-top: 12px;
    margin-bottom: 8px;
    color: var(--text-primary, #2c3e50);
}

.output-card-content p {
    margin: 8px 0;
}

.output-card-content ul {
    margin: 8px 0;
    padding-left: 20px;
}

.output-card-content li {
    margin: 4px 0;
}
</style>
'''

# Global formatter instance
output_formatter = OutputFormatter()
