"""
Business Analyst - AI-powered data introspection and strategic reasoning
Converts raw SQL results into actionable business insights
"""
import ollama
import pandas as pd

class BusinessAnalyst:
    def __init__(self):
        self.model = "mistral:7b-instruct"
    
    def analyze_trends(self, df: pd.DataFrame) -> str:
        """
        Detect growth patterns and trends in data
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            One-line trend summary
        """
        if df is None or df.empty or len(df) < 2:
            return "Insufficient data for trend analysis."
        
        # Try to find numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return "No numeric data for trend analysis."
        
        # Analyze first numeric column
        col = numeric_cols[0]
        values = df[col].dropna()
        
        if len(values) < 2:
            return "Insufficient numeric data."
        
        # Calculate trend
        first_val = values.iloc[0]
        last_val = values.iloc[-1]
        
        if first_val == 0:
            return f"Growing from {first_val} to {last_val}"
        
        change_pct = ((last_val - first_val) / first_val) * 100
        
        if abs(change_pct) < 1:
            return "Stable (minimal change)"
        elif change_pct > 0:
            return f"Increasing trend (+{change_pct:.1f}% growth)"
        else:
            return f"Declining trend ({change_pct:.1f}% decrease)"
    
    def analyze_results_with_llm(self, question: str, df: pd.DataFrame, sql: str = None) -> dict:
        """
        Analyze SQL query results and provide business insights
        
        Args:
            question: Original user question
            df: DataFrame with query results
            sql: SQL query that was executed (optional)
        
        Returns:
            dict with 'insight', 'summary', 'recommendations'
        """
        if df is None or df.empty:
            return {
                'insight': "No data was found for your query.",
                'summary': "The query returned no results.",
                'recommendations': []
            }
        
        # Prepare data summary for LLM
        data_summary = self._prepare_data_summary(df)
        
        # Build analysis prompt
        prompt = f"""You are a senior business analyst reviewing query results.

User Question: "{question}"

Data Retrieved:
{data_summary}

Your task:
1. Provide a clear, concise insight about what this data shows
2. Identify key trends, patterns, or notable findings
3. Offer 2-3 actionable business recommendations based on this data

Format your response as:

INSIGHT:
[One paragraph summarizing the key finding]

KEY OBSERVATIONS:
- [Observation 1]
- [Observation 2]
- [Observation 3]

RECOMMENDATIONS:
- [Actionable recommendation 1]
- [Actionable recommendation 2]
- [Actionable recommendation 3]

Keep it professional, data-driven, and actionable. Focus on business value."""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior business analyst with expertise in data interpretation and strategic recommendations. You provide clear, actionable insights based on data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            analysis = response['message']['content']
            
            # Parse the response
            parsed = self._parse_analysis(analysis)
            
            return {
                'insight': parsed.get('insight', analysis),
                'summary': self._generate_summary(df),
                'recommendations': parsed.get('recommendations', []),
                'full_analysis': analysis
            }
            
        except Exception as e:
            return {
                'insight': f"Analysis unavailable: {str(e)}",
                'summary': self._generate_summary(df),
                'recommendations': []
            }
    
    def _prepare_data_summary(self, df: pd.DataFrame) -> str:
        """
        Prepare a concise summary of the DataFrame for LLM analysis
        """
        summary_parts = []
        
        # Basic info
        summary_parts.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        summary_parts.append(f"Columns: {', '.join(df.columns.tolist())}")
        
        # For small datasets, include all data
        if len(df) <= 10:
            summary_parts.append("\nFull Data:")
            summary_parts.append(df.to_string(index=False))
        else:
            # For larger datasets, provide summary statistics
            summary_parts.append("\nFirst 5 rows:")
            summary_parts.append(df.head(5).to_string(index=False))
            
            summary_parts.append("\nLast 5 rows:")
            summary_parts.append(df.tail(5).to_string(index=False))
            
            # Add numeric column statistics
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary_parts.append("\nNumeric Statistics:")
                summary_parts.append(df[numeric_cols].describe().to_string())
        
        return "\n".join(summary_parts)
    
    def _generate_summary(self, df: pd.DataFrame) -> str:
        """
        Generate a simple text summary of the data
        """
        if df.empty:
            return "No data found."
        
        row_count = len(df)
        col_count = len(df.columns)
        
        return f"Retrieved {row_count} record{'s' if row_count != 1 else ''} with {col_count} column{'s' if col_count != 1 else ''}."
    
    def _parse_analysis(self, analysis: str) -> dict:
        """
        Parse the LLM analysis response into structured components
        """
        result = {
            'insight': '',
            'observations': [],
            'recommendations': []
        }
        
        # Extract insight section
        insight_match = analysis.split('INSIGHT:')
        if len(insight_match) > 1:
            insight_text = insight_match[1].split('KEY OBSERVATIONS:')[0].strip()
            result['insight'] = insight_text
        
        # Extract recommendations
        if 'RECOMMENDATIONS:' in analysis:
            rec_section = analysis.split('RECOMMENDATIONS:')[1]
            recommendations = [line.strip('- ').strip() for line in rec_section.split('\n') if line.strip().startswith('-')]
            result['recommendations'] = recommendations
        
        # If parsing fails, use the full analysis as insight
        if not result['insight']:
            result['insight'] = analysis
        
        return result
    
    def compare_periods(self, question: str, df: pd.DataFrame) -> str:
        """
        Specialized analysis for period-over-period comparisons
        """
        if df is None or df.empty or len(df) < 2:
            return "Insufficient data for comparison."
        
        # Detect if this is a comparison query
        comparison_keywords = ['compare', 'vs', 'versus', 'compared to', 'year-over-year', 'yoy']
        is_comparison = any(keyword in question.lower() for keyword in comparison_keywords)
        
        if not is_comparison:
            return None
        
        # Try to identify numeric columns for comparison
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return None
        
        # Simple comparison logic
        if len(df) == 2:
            col = numeric_cols[0]
            val1, val2 = df[col].iloc[0], df[col].iloc[1]
            
            if val1 > 0:
                change_pct = ((val2 - val1) / val1) * 100
                direction = "increased" if change_pct > 0 else "decreased"
                
                return f"The data shows a {direction} of {abs(change_pct):.1f}% between the two periods."
        
        return None

# Global analyst instance
analyst = BusinessAnalyst()
