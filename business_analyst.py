"""
Business Analyst - DB-INTELLIGENCE-V1 Hybrid Intelligence Engine
Combines strict SQL accuracy with advanced business reasoning and strategic insights
Converts raw SQL results into actionable business intelligence
"""
import re
import ollama
import pandas as pd
from hybrid_reasoner import HybridReasoner

class BusinessAnalyst:
    def __init__(self):
        self.model = "mistral:7b-instruct"
        self.hybrid_reasoner = HybridReasoner()
        
        self.cagr_keywords = ['cagr', 'compound annual growth', 'growth rate', 'annual growth']
        self.forecast_keywords = ['forecast', 'project', 'predict', 'future', 'scenario', 'projection', 'estimate']
        
        # Person/entity detection keywords
        self.person_keywords = ['tell me about', 'who is', 'what company', 'phone number', 'email', 'contact', 'works at', 'employee']
        
        # Metric detection keywords
        self.metric_keywords = {
            'growth': ['growth', 'increase', 'decrease', 'change', 'difference'],
            'ratio': ['ratio', 'proportion', 'per', 'divide'],
            'share': ['share', 'percentage', 'percent', 'portion', 'contribution'],
            'aov': ['average order value', 'aov', 'average per order', 'mean order'],
            'compare': ['compare', 'comparison', 'versus', 'vs', 'against']
        }
    
    def detect_person_query(self, question: str) -> bool:
        """
        Detect if the query is asking about a specific person
        
        Args:
            question: User's question
        
        Returns:
            True if asking about a person
        """
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in self.person_keywords)
    
    def detect_cagr_query(self, question: str) -> bool:
        """
        Detect if the query is asking for CAGR calculation
        
        Args:
            question: User's question
        
        Returns:
            True if CAGR-related query
        """
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in self.cagr_keywords)
    
    def detect_forecast_query(self, question: str) -> bool:
        """
        Detect if the query is asking for forecasting
        
        Args:
            question: User's question
        
        Returns:
            True if forecast-related query
        """
        question_lower = question.lower()
        
        # Check for forecast keywords
        if any(keyword in question_lower for keyword in self.forecast_keywords):
            return True
        
        # Check for "will be" pattern (e.g., "What will sales be in 2025?")
        if "will" in question_lower and ("be" in question_lower or "sales" in question_lower):
            return True
        
        return False
    
    def extract_years_from_query(self, question: str) -> tuple:
        """
        Extract start and end years from query
        
        Args:
            question: User's question
        
        Returns:
            Tuple of (start_year, end_year) or (None, None)
        """
        # Find all 4-digit years in the question
        years = re.findall(r'\b(20\d{2})\b', question)
        
        if len(years) >= 2:
            years = [int(y) for y in years]
            years.sort()
            return (years[0], years[-1])
        
        return (None, None)
    
    def extract_forecast_years(self, question: str) -> list:
        """
        Extract forecast target years from query
        
        Args:
            question: User's question
        
        Returns:
            List of forecast years (e.g., [2025, 2026])
        """
        from datetime import datetime
        
        # Find all 4-digit years in the question
        years = re.findall(r'\b(20\d{2})\b', question)
        years = [int(y) for y in years]
        
        # Filter for future years only
        current_year = datetime.now().year
        forecast_years = [y for y in years if y > current_year]
        
        # If no explicit years, default to next 2 years
        if not forecast_years and self.detect_forecast_query(question):
            forecast_years = [current_year + 1, current_year + 2]
        
        return sorted(list(set(forecast_years)))
    
    def detect_trend(self, series) -> str:
        """
        Detect trend direction from a numeric series
        
        Args:
            series: Pandas Series or list of numeric values
        
        Returns:
            "upward", "downward", or "stable"
        """
        if series is None or len(series) < 2:
            return "stable"
        
        try:
            # Convert to list if needed
            if hasattr(series, 'tolist'):
                values = series.tolist()
            else:
                values = list(series)
            
            # Compare last two values
            if values[-1] > values[-2]:
                return "upward"
            elif values[-1] < values[-2]:
                return "downward"
            else:
                return "stable"
        except Exception:
            return "stable"
    
    def analyze_trends(self, df: pd.DataFrame) -> str:
        """
        Detect growth patterns and trends in data
        DB-ANALYST-V3: NO CALCULATIONS - only describe direction using exact values
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            One-line trend summary with direction (NO percentages, NO calculations)
        """
        if df is None or df.empty or len(df) < 2:
            return "Insufficient data for trend analysis."
        
        # Try to find numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return "No numeric data for trend analysis."
        
        # Analyze first numeric column (skip Year/Period columns)
        col = numeric_cols[0]
        if 'year' in col.lower() or 'period' in col.lower() or 'date' in col.lower():
            if len(numeric_cols) > 1:
                col = numeric_cols[1]
        
        values = df[col].dropna()
        
        if len(values) < 2:
            return "Insufficient numeric data."
        
        # Detect trend direction
        trend_direction = self.detect_trend(values)
        
        # Get exact first and last values (NO CALCULATIONS)
        first_val = values.iloc[0]
        last_val = values.iloc[-1]
        
        # Format trend with emoji - ONLY state direction and exact values
        trend_emoji = {
            'upward': '📈',
            'downward': '📉',
            'stable': '➖'
        }
        
        emoji = trend_emoji.get(trend_direction, '')
        
        # DB-ANALYST-V3: NO percentage calculations, only exact values
        if trend_direction == 'upward':
            return f"Trend: Upward {emoji} (from {first_val} to {last_val})"
        elif trend_direction == 'downward':
            return f"Trend: Downward {emoji} (from {first_val} to {last_val})"
        else:
            return f"Trend: Stable {emoji} ({first_val} to {last_val})"
    
    def analyze_with_cagr(self, question: str, df: pd.DataFrame, cagr_result: dict) -> dict:
        """
        Analyze results with CAGR calculation from database
        NO LLM COMPUTATION - Only commentary on database-returned numbers
        
        Args:
            question: User's question
            df: DataFrame with query results
            cagr_result: CAGR calculation result from SQL
        
        Returns:
            dict with analysis including CAGR and forecasts
        """
        if not cagr_result['success']:
            return {
                'insight': f"Could not calculate CAGR: {cagr_result['message']}",
                'summary': "CAGR calculation failed",
                'recommendations': [],
                'cagr': None,
                'has_forecast': False
            }
        
        cagr = cagr_result['cagr']
        start_year = cagr_result['start_year']
        end_year = cagr_result['end_year']
        start_sales = cagr_result['start_sales']
        end_sales = cagr_result['end_sales']
        
        # Build insight using exact database values - NO MATH
        insight = f"The Compound Annual Growth Rate (CAGR) from {start_year} to {end_year} is {cagr}%. "
        insight += f"Sales grew from {start_sales:.2f} in {start_year} to {end_sales:.2f} in {end_year}."
        
        # Add forecast insight if available
        has_forecast = bool(cagr_result.get('forecast'))
        if has_forecast:
            forecast_years = sorted(cagr_result['forecast'].keys())
            insight += f" Based on this CAGR, forecasts have been calculated for {', '.join(map(str, forecast_years))}."
        
        # Recommendations based on CAGR value (qualitative only, no math)
        if cagr > 10:
            growth_desc = "strong"
            recommendation = "Continue current strategies and explore expansion opportunities."
        elif cagr > 5:
            growth_desc = "moderate"
            recommendation = "Identify areas for acceleration and optimize operations."
        else:
            growth_desc = "slow"
            recommendation = "Review strategies and consider new growth initiatives."
        
        recommendations = [
            f"The {cagr}% CAGR indicates {growth_desc} growth over this period.",
            recommendation,
            "Monitor this growth rate against industry benchmarks."
        ]
        
        return {
            'insight': insight,
            'summary': f"CAGR: {cagr}% ({start_year}-{end_year})",
            'recommendations': recommendations,
            'cagr': cagr,
            'has_forecast': has_forecast,
            'forecast': cagr_result.get('forecast', {}),
            'scenarios': cagr_result.get('scenarios', {}),
            'cagr_details': {
                'start_year': start_year,
                'end_year': end_year,
                'start_sales': start_sales,
                'end_sales': end_sales
            }
        }
    
    def check_person_in_database(self, name: str) -> dict:
        """
        Check if a person exists in employees or customers tables
        MUST be called before providing any information about a person
        
        Args:
            name: Person's name to search for
        
        Returns:
            dict with 'found', 'table', 'data', 'message'
        """
        import mysql.connector
        from common import AppConfig
        
        result = {
            'found': False,
            'table': None,
            'data': None,
            'message': ''
        }
        
        try:
            conn = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_NAME
            )
            cursor = conn.cursor(dictionary=True)
            
            # Split name into parts
            name_parts = name.strip().split()
            
            if len(name_parts) >= 2:
                first_name = name_parts[0]
                last_name = name_parts[-1]
                
                # Search employees
                cursor.execute(
                    "SELECT * FROM employees WHERE FirstName = %s AND LastName = %s",
                    (first_name, last_name)
                )
                employee = cursor.fetchone()
                
                if employee:
                    result['found'] = True
                    result['table'] = 'employees'
                    result['data'] = employee
                    result['message'] = f"Found in employees table"
                    conn.close()
                    return result
            
            # Search customers (ContactPerson field)
            cursor.execute(
                "SELECT * FROM customers WHERE ContactPerson LIKE %s",
                (f"%{name}%",)
            )
            customer = cursor.fetchone()
            
            if customer:
                result['found'] = True
                result['table'] = 'customers'
                result['data'] = customer
                result['message'] = f"Found in customers table"
            else:
                result['message'] = f"This person does not exist in your database."
            
            conn.close()
            return result
            
        except Exception as e:
            result['message'] = f"Database search error: {str(e)}"
            return result
    
    def analyze_with_hybrid_intelligence(self, question: str, df: pd.DataFrame, sql: str = None) -> dict:
        """
        DB-INTELLIGENCE-V1: Hybrid analysis combining SQL accuracy with business reasoning
        
        Args:
            question: Original user question
            df: DataFrame with query results (can be empty)
            sql: SQL query that was executed
        
        Returns:
            dict with 'sql_result', 'insight', 'recommendation', 'sql_query'
        """
        # Prepare SQL result summary
        if df is None or df.empty:
            sql_result_summary = "No data found matching the query criteria."
            query_context = {'empty': True, 'sql': sql}
        else:
            sql_result_summary = self._format_sql_result(df)
            query_context = {'empty': False, 'sql': sql, 'row_count': len(df)}
        
        # Use hybrid reasoner to interpret results
        reasoning = self.hybrid_reasoner.interpret_result(df, query_context, question)
        
        return {
            'sql_result': sql_result_summary,
            'insight': reasoning['insight'],
            'recommendation': reasoning['recommendation'],
            'sql_query': sql,
            'framework_used': reasoning.get('framework_used', 'default'),
            'raw_data': df
        }
    
    def _format_sql_result(self, df: pd.DataFrame) -> str:
        """Format SQL result for display"""
        if df is None or df.empty:
            return "No data found."
        
        if len(df) <= 10:
            return df.to_string(index=False)
        else:
            return f"{df.head(10).to_string(index=False)}\n\n... ({len(df)} total rows)"
    
    def analyze_results_with_llm(self, question: str, df: pd.DataFrame, sql: str = None) -> dict:
        """
        Analyze SQL query results and provide business insights
        DB-ANALYST-V3 ULTRA-STRICT MODE: Only use actual data from the DataFrame
        NO calculations, NO fabrication, NO external knowledge
        
        Args:
            question: Original user question
            df: DataFrame with query results
            sql: SQL query that was executed (optional)
        
        Returns:
            dict with 'insight', 'summary', 'recommendations', 'raw_data'
        """
        if df is None or df.empty:
            return {
                'insight': "No data available for this query in the current database.",
                'summary': "The query returned no results.",
                'recommendations': [],
                'raw_data': None
            }
        
        # Prepare data summary for LLM
        data_summary = self._prepare_data_summary(df)
        
        # Build analysis prompt with DB-ANALYST-V3 ULTRA-STRICT instructions
        prompt = f"""You are DB-ANALYST-V3, a STRICT database-only analyst.

🔐 ABSOLUTE RULES (VIOLATION = FAILURE):

1. You ONLY describe what appears in the SQL RESULT below
2. ❌ NEVER calculate ANY number (no %, no growth, no averages, no differences)
3. ❌ NEVER use external knowledge (no actors, no companies, no world facts)
4. ❌ NEVER invent or assume ANY value
5. ✔ ONLY copy exact numbers from the data
6. If asked about someone/something not in data → say "does not exist in your database"
7. NO math, NO world knowledge, NO assumptions, NO calculations

User Question: "{question}"

SQL RESULT (YOUR ONLY SOURCE OF TRUTH):
{data_summary}

Your task:
- Restate what the SQL RESULT shows using EXACT values only
- Compare values if both are present (e.g., "X is higher than Y")
- NO percentages, NO growth rates, NO calculations of any kind

FORBIDDEN EXAMPLES:
❌ "Growth rate is 15%" (unless 15 appears in SQL RESULT)
❌ "Average is 500" (unless 500 appears in SQL RESULT)
❌ "Increased by 20%" (unless 20 appears in SQL RESULT)
❌ "Shah Rukh Khan is a Bollywood actor" (external knowledge)

ALLOWED EXAMPLES:
✔ "The data shows: 2023 sales = 100, 2024 sales = 150"
✔ "Customer A has 500, Customer B has 300. A is higher."
✔ "The highest value in the table is 200"

Output format:
INSIGHT: [One sentence restating exact data]
OBSERVATIONS: [2-3 bullet points with exact numbers from SQL RESULT]
RECOMMENDATIONS: [Actionable suggestions based on observations, NO calculations]

NO MARKDOWN. NO CALCULATIONS. EXACT DATA ONLY."""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are DB-ANALYST-V3. ABSOLUTE RULE: You ONLY use exact data from SQL RESULT. You NEVER calculate, fabricate, assume, or use external knowledge. Every number you mention MUST appear EXACTLY in the SQL RESULT. NO MATH. NO EXTERNAL KNOWLEDGE. VIOLATION = FAILURE."
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
                'full_analysis': analysis,
                'raw_data': df  # Include raw data for verification
            }
            
        except Exception as e:
            return {
                'insight': f"Analysis unavailable: {str(e)}",
                'summary': self._generate_summary(df),
                'recommendations': [],
                'raw_data': df
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
    
    def detect_metrics(self, query: str) -> list:
        """
        Detect which metrics the user is asking for
        
        Args:
            query: User's question
        
        Returns:
            List of detected metric types
        """
        query_lower = query.lower()
        detected = []
        
        for metric_type, keywords in self.metric_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected.append(metric_type)
        
        return detected
    
    def calculate_metric(self, df: pd.DataFrame, metric_type: str, query: str = "") -> pd.DataFrame:
        """
        Calculate specified metric using numeric columns from DataFrame
        
        Args:
            df: DataFrame with data
            metric_type: Type of metric ('growth', 'ratio', 'share', 'aov', 'cagr')
            query: Original query for context (optional)
        
        Returns:
            DataFrame with ComputedMetric column added
        """
        if df is None or df.empty:
            return df
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) == 0:
            return df
        
        # Make a copy to avoid modifying original
        result_df = df.copy()
        
        try:
            if metric_type == 'growth':
                # Calculate growth percentage between first and last numeric values
                if len(numeric_cols) >= 1 and len(df) >= 2:
                    # Use the first numeric column (skip Year/Period columns if they exist)
                    col = numeric_cols[0]
                    # If first column looks like a year/period, use second column
                    if 'year' in col.lower() or 'period' in col.lower() or 'date' in col.lower():
                        if len(numeric_cols) > 1:
                            col = numeric_cols[1]
                    
                    v1 = float(df[col].iloc[0])
                    v2 = float(df[col].iloc[-1])
                    
                    if v1 != 0:
                        growth = ((v2 - v1) / v1) * 100
                        # Add as a single computed value (not per row)
                        result_df.loc[result_df.index[0], 'ComputedMetric'] = growth
                        result_df.loc[result_df.index[0], 'MetricType'] = 'Growth%'
                        result_df.loc[result_df.index[0], 'MetricFormula'] = f'(({v2} - {v1}) / {v1}) * 100'
            
            elif metric_type == 'ratio':
                # Calculate ratio between two numeric columns
                if len(numeric_cols) >= 2:
                    col1, col2 = numeric_cols[0], numeric_cols[1]
                    result_df['ComputedMetric'] = df[col1] / df[col2]
                    result_df['MetricType'] = f'{col1}/{col2} Ratio'
                    result_df['MetricFormula'] = f'{col1} / {col2}'
            
            elif metric_type == 'share':
                # Calculate percentage share of total
                if len(numeric_cols) >= 1:
                    col = numeric_cols[0]
                    total = df[col].sum()
                    if total != 0:
                        result_df['ComputedMetric'] = (df[col] / total) * 100
                        result_df['MetricType'] = 'Share%'
                        result_df['MetricFormula'] = f'(value / total) * 100'
            
            elif metric_type == 'aov':
                # Calculate Average Order Value
                # Look for TotalAmount and OrderID or similar columns
                amount_cols = [c for c in numeric_cols if 'amount' in c.lower() or 'total' in c.lower() or 'revenue' in c.lower()]
                order_cols = [c for c in numeric_cols if 'order' in c.lower() or 'count' in c.lower() or 'quantity' in c.lower()]
                
                if amount_cols and order_cols:
                    amount_col = amount_cols[0]
                    order_col = order_cols[0]
                    result_df['ComputedMetric'] = df[amount_col] / df[order_col]
                    result_df['MetricType'] = 'AOV'
                    result_df['MetricFormula'] = f'{amount_col} / {order_col}'
                elif amount_cols:
                    # If only amount, calculate mean
                    aov = df[amount_cols[0]].mean()
                    result_df['ComputedMetric'] = aov
                    result_df['MetricType'] = 'Average'
                    result_df['MetricFormula'] = f'MEAN({amount_cols[0]})'
            
            elif metric_type == 'compare':
                # Calculate percentage difference for comparison
                if len(numeric_cols) >= 1 and len(df) >= 2:
                    col = numeric_cols[0]
                    # Calculate pairwise percentage differences
                    result_df['ComputedMetric'] = df[col].pct_change() * 100
                    result_df['MetricType'] = 'Change%'
                    result_df['MetricFormula'] = 'pct_change() * 100'
        
        except Exception as e:
            print(f"[WARNING] Metric calculation failed for {metric_type}: {e}")
            return df
        
        return result_df
    
    def apply_metrics(self, df: pd.DataFrame, query: str) -> pd.DataFrame:
        """
        Detect and apply relevant metrics to DataFrame
        
        Args:
            df: DataFrame with data
            query: User's question
        
        Returns:
            DataFrame with computed metrics added
        """
        if df is None or df.empty:
            return df
        
        # Detect which metrics to calculate
        detected_metrics = self.detect_metrics(query)
        
        if not detected_metrics:
            return df
        
        # Apply the first detected metric
        # (could be extended to apply multiple metrics)
        metric_type = detected_metrics[0]
        
        return self.calculate_metric(df, metric_type, query)
    
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
