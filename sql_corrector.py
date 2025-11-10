"""
SQL Corrector - Schema-aware SQL validation and auto-correction
Handles column name mismatches and alias errors automatically
"""
import re
import mysql.connector
from common import AppConfig

class SQLCorrector:
    def __init__(self):
        self.schema_cache = {}
        self.load_schema()
    
    def load_schema(self):
        """
        Load database schema (tables and columns) into cache
        """
        try:
            conn = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_NAME
            )
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get columns for each table
            for table in tables:
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [row[0] for row in cursor.fetchall()]
                self.schema_cache[table] = columns
            
            conn.close()
            print(f"✓ Loaded schema: {len(tables)} tables")
            
        except Exception as e:
            print(f"⚠ Warning: Could not load schema: {e}")
            self.schema_cache = {}
    
    def validate_sql(self, sql: str) -> dict:
        """
        Validate SQL against schema
        Returns: dict with 'valid', 'errors', 'suggestions'
        """
        errors = []
        suggestions = []
        
        # Extract table and column references from SQL
        # This is a simplified validation - can be enhanced
        
        # Check for common patterns
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        where_pattern = r'WHERE\s+(.*?)(?:GROUP|ORDER|LIMIT|;|$)'
        
        select_match = re.search(select_pattern, sql, re.IGNORECASE | re.DOTALL)
        where_match = re.search(where_pattern, sql, re.IGNORECASE | re.DOTALL)
        
        # Extract column references
        columns_referenced = []
        if select_match:
            select_clause = select_match.group(1)
            # Simple extraction - can be improved
            cols = re.findall(r'(\w+\.\w+|\w+)', select_clause)
            columns_referenced.extend(cols)
        
        if where_match:
            where_clause = where_match.group(1)
            cols = re.findall(r'(\w+\.\w+)', where_clause)
            columns_referenced.extend(cols)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions,
            'columns_referenced': columns_referenced
        }
    
    def extract_error_column(self, error_message: str) -> str:
        """
        Extract the problematic column name from MySQL error message
        Example: "Unknown column 'c.CustomerID' in 'field list'"
        Returns: 'CustomerID' or the full reference
        """
        # Pattern for "Unknown column 'xxx' in 'yyy'"
        match = re.search(r"Unknown column '([^']+)'", error_message)
        if match:
            column_ref = match.group(1)
            # If it's aliased (e.g., 'c.CustomerID'), extract just the column name
            if '.' in column_ref:
                return column_ref.split('.')[-1]
            return column_ref
        return None
    
    def find_column_in_schema(self, column_name: str) -> list:
        """
        Find which table(s) contain the given column
        Returns: list of (table, column) tuples
        """
        matches = []
        column_lower = column_name.lower()
        
        for table, columns in self.schema_cache.items():
            for col in columns:
                if col.lower() == column_lower:
                    matches.append((table, col))
        
        return matches
    
    def correct_sql(self, sql: str, error_message: str) -> dict:
        """
        Attempt to auto-correct SQL based on error message
        Returns: dict with 'corrected_sql', 'success', 'explanation'
        """
        # Check if it's an unknown column error (MySQL error 1054)
        if 'Unknown column' not in error_message and '1054' not in str(error_message):
            return {
                'corrected_sql': None,
                'success': False,
                'explanation': 'Not an unknown column error'
            }
        
        # Extract the problematic column
        error_column = self.extract_error_column(error_message)
        if not error_column:
            return {
                'corrected_sql': None,
                'success': False,
                'explanation': 'Could not parse error column'
            }
        
        # Find the column in schema
        matches = self.find_column_in_schema(error_column)
        
        if not matches:
            return {
                'corrected_sql': None,
                'success': False,
                'explanation': f"Column '{error_column}' not found in any table"
            }
        
        if len(matches) > 1:
            # Multiple tables have this column - try to infer from context
            # For now, use the first match
            table, column = matches[0]
            explanation = f"Column '{error_column}' found in multiple tables, using {table}.{column}"
        else:
            table, column = matches[0]
            explanation = f"Corrected to use {table}.{column}"
        
        # Attempt to correct the SQL
        # Replace incorrect references with correct table.column
        corrected_sql = sql
        
        # Pattern 1: Replace alias.column with table.column
        # Example: c.CustomerID -> customers.CustomerID
        pattern1 = re.compile(r'\b\w+\.' + re.escape(error_column) + r'\b', re.IGNORECASE)
        corrected_sql = pattern1.sub(f'{table}.{column}', corrected_sql)
        
        # Pattern 2: Replace bare column name with table.column
        pattern2 = re.compile(r'\b' + re.escape(error_column) + r'\b(?!\s*\()', re.IGNORECASE)
        corrected_sql = pattern2.sub(f'{table}.{column}', corrected_sql)
        
        return {
            'corrected_sql': corrected_sql,
            'success': True,
            'explanation': explanation,
            'original_column': error_column,
            'corrected_to': f'{table}.{column}'
        }
    
    def execute_with_retry(self, sql: str, max_retries: int = 1) -> dict:
        """
        Execute SQL with automatic retry and correction on error
        Returns: dict with 'success', 'data', 'sql_used', 'correction_applied', 'message'
        """
        import pandas as pd
        
        result = {
            'success': False,
            'data': None,
            'sql_used': sql,
            'correction_applied': False,
            'original_sql': sql,
            'message': ''
        }
        
        for attempt in range(max_retries + 1):
            try:
                conn = mysql.connector.connect(
                    host=AppConfig.DB_HOST,
                    user=AppConfig.DB_USER,
                    password=AppConfig.DB_PASSWORD,
                    database=AppConfig.DB_NAME
                )
                
                df = pd.read_sql_query(sql, conn)
                conn.close()
                
                result['success'] = True
                result['data'] = df
                result['sql_used'] = sql
                
                if attempt > 0:
                    result['message'] = '⚙️ Auto-corrected SQL and executed successfully.'
                else:
                    result['message'] = '✓ SQL executed successfully.'
                
                return result
                
            except mysql.connector.Error as e:
                error_code = e.errno
                error_message = str(e)
                
                print(f"SQL Error (attempt {attempt + 1}): {error_message}")
                
                # If this is the last attempt, return the error
                if attempt >= max_retries:
                    result['message'] = f'❌ SQL execution failed: {error_message}'
                    return result
                
                # Try to correct the SQL
                correction = self.correct_sql(sql, error_message)
                
                if correction['success'] and correction['corrected_sql']:
                    print(f"Attempting correction: {correction['explanation']}")
                    sql = correction['corrected_sql']
                    result['correction_applied'] = True
                    result['sql_used'] = sql
                else:
                    result['message'] = f"❌ Column not found in schema. {correction['explanation']}"
                    return result
            
            except Exception as e:
                result['message'] = f'❌ Unexpected error: {str(e)}'
                return result
        
        return result

# Global corrector instance
corrector = SQLCorrector()
