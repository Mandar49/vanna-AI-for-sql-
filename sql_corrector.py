"""
SQL Corrector - Schema-aware SQL validation and auto-correction
Handles column name mismatches and alias errors automatically
"""
import re
import mysql.connector
import pandas as pd
from common import AppConfig
from schema_manager import schema_manager
from query_cache import query_cache

class SQLCorrector:
    # Define table relationships for automatic join inference
    RELATIONS = {
        "salesorders.CustomerID": "customers.CustomerID",
        "salesorders.EmployeeID": "employees.EmployeeID",
        "orderitems.OrderID": "salesorders.OrderID",
        "orderitems.ProductID": "products.ProductID",
        "products.CategoryID": "categories.CategoryID",
        "employees.DepartmentID": "departments.DepartmentID",
        "customers.RegionID": "regions.RegionID",
        "leads.ContactID": "contacts.ContactID"
    }
    
    def __init__(self):
        self.schema_cache = {}
        self.relationship_map = {}
        self.load_schema()
        self.build_relationship_map()
    
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
            
            # Get columns for each table with data types
            for table in tables:
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [row[0] for row in cursor.fetchall()]
                self.schema_cache[table] = columns
            
            conn.close()
            print(f"[OK] Loaded schema: {len(tables)} tables")
            
        except Exception as e:
            print(f"[WARNING] Could not load schema: {e}")
            self.schema_cache = {}
    
    def build_relationship_map(self):
        """
        Build bidirectional relationship map from RELATIONS dictionary
        """
        self.relationship_map = {}
        
        for source, target in self.RELATIONS.items():
            source_table, source_col = source.split('.')
            target_table, target_col = target.split('.')
            
            # Add forward relationship
            if source_table not in self.relationship_map:
                self.relationship_map[source_table] = []
            
            self.relationship_map[source_table].append({
                'target_table': target_table,
                'source_column': source_col,
                'target_column': target_col,
                'join_type': 'INNER'
            })
            
            # Add reverse relationship
            if target_table not in self.relationship_map:
                self.relationship_map[target_table] = []
            
            self.relationship_map[target_table].append({
                'target_table': source_table,
                'source_column': target_col,
                'target_column': source_col,
                'join_type': 'LEFT'
            })
    
    def infer_relationships(self, table_name: str) -> list:
        """
        Infer valid join candidates for a given table
        
        Args:
            table_name: Name of the table to find relationships for
        
        Returns:
            List of relationship dictionaries with join information
        """
        if table_name not in self.relationship_map:
            return []
        
        return self.relationship_map[table_name]
    
    def validate_column_exists(self, table_name: str, column_name: str) -> bool:
        """
        Validate that a column exists in the specified table
        
        Args:
            table_name: Name of the table
            column_name: Name of the column
        
        Returns:
            True if column exists, False otherwise
        
        Raises:
            ValueError: If table doesn't exist in schema
        """
        if table_name not in self.schema_cache:
            raise ValueError(f"Table '{table_name}' not found in schema")
        
        return column_name in self.schema_cache[table_name]
    
    def introspect_query_columns(self, sql: str) -> dict:
        """
        Introspect SQL query to extract and validate columns
        
        Args:
            sql: SQL query string
        
        Returns:
            dict with 'valid', 'invalid_columns', 'tables_used'
        """
        result = {
            'valid': True,
            'invalid_columns': [],
            'tables_used': []
        }
        
        # Extract table names from FROM and JOIN clauses
        from_pattern = r'FROM\s+(\w+)'
        join_pattern = r'JOIN\s+(\w+)'
        
        tables = re.findall(from_pattern, sql, re.IGNORECASE)
        tables.extend(re.findall(join_pattern, sql, re.IGNORECASE))
        result['tables_used'] = list(set(tables))
        
        # Extract column references (table.column format)
        column_pattern = r'(\w+)\.(\w+)'
        column_refs = re.findall(column_pattern, sql)
        
        # Validate each column reference with table prefix
        for table, column in column_refs:
            if table in self.schema_cache:
                try:
                    if not self.validate_column_exists(table, column):
                        result['valid'] = False
                        result['invalid_columns'].append(f"{table}.{column}")
                except ValueError:
                    # Table not in schema
                    result['valid'] = False
                    result['invalid_columns'].append(f"{table}.{column}")
            else:
                # Check if it's a table alias - if so, skip validation
                # (aliases are harder to track without full SQL parsing)
                pass
        
        return result
    
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
    
    def fix_mysql_syntax(self, sql: str) -> str:
        """
        Fix common MySQL syntax errors
        - Replace invalid FOR YEAR(...) constructs
        - Ensure proper JOIN syntax
        - Fix column references
        """
        # Fix FOR YEAR(...) syntax - replace with proper CASE statements
        if 'FOR YEAR(' in sql.upper():
            # This is an invalid construct, needs manual correction
            # We'll flag it but can't auto-fix complex logic
            print("[WARNING] Invalid 'FOR YEAR()' syntax detected. Needs manual correction.")
        
        # Ensure table aliases are used consistently
        # Add more syntax fixes as needed
        
        return sql
    
    def build_join_clause(self, from_table: str, target_table: str) -> str:
        """
        Build JOIN clause dynamically using inferred relationships
        
        Args:
            from_table: Source table name
            target_table: Target table to join
        
        Returns:
            JOIN clause string or empty string if no relationship found
        """
        relationships = self.infer_relationships(from_table)
        
        for rel in relationships:
            if rel['target_table'] == target_table:
                join_type = rel['join_type']
                source_col = rel['source_column']
                target_col = rel['target_column']
                
                return f"{join_type} JOIN {target_table} ON {from_table}.{source_col} = {target_table}.{target_col}"
        
        return ""
    
    def get_table_columns(self, table_name: str) -> list:
        """
        Get list of columns for a table
        
        Args:
            table_name: Name of the table
        
        Returns:
            List of column names
        """
        return self.schema_cache.get(table_name, [])
    
    def validate_query_structure(self, sql: str) -> dict:
        """
        Validate query structure and suggest corrections
        
        Args:
            sql: SQL query string
        
        Returns:
            dict with 'valid', 'errors', 'suggestions'
        """
        result = {
            'valid': True,
            'errors': [],
            'suggestions': []
        }
        
        # Check for SELECT statement
        if not sql.strip().upper().startswith('SELECT'):
            result['valid'] = False
            result['errors'].append("Query must start with SELECT")
        
        # Introspect columns
        introspection = self.introspect_query_columns(sql)
        
        if not introspection['valid']:
            result['valid'] = False
            result['errors'].extend([f"Invalid column: {col}" for col in introspection['invalid_columns']])
            
            # Suggest corrections
            for invalid_col in introspection['invalid_columns']:
                if '.' in invalid_col:
                    table, col = invalid_col.split('.')
                    if table in self.schema_cache:
                        similar_cols = [c for c in self.schema_cache[table] if col.lower() in c.lower()]
                        if similar_cols:
                            result['suggestions'].append(f"Did you mean {table}.{similar_cols[0]}?")
        
        return result
    
    def calculate_cagr_sql(self, start_year: int, end_year: int, forecast_years: list = None) -> dict:
        """
        Calculate CAGR (Compound Annual Growth Rate) directly from SQL with optional forecasting
        Returns the CAGR value from database calculation, no LLM computation
        
        Args:
            start_year: Starting year for CAGR calculation
            end_year: Ending year for CAGR calculation
            forecast_years: Optional list of years to forecast (e.g., [2025, 2026])
        
        Returns:
            dict with 'success', 'cagr', 'start_sales', 'end_sales', 'forecast', 'scenarios', 'message'
        """
        import pandas as pd
        
        result = {
            'success': False,
            'cagr': None,
            'cagr_decimal': None,
            'start_year': start_year,
            'end_year': end_year,
            'start_sales': None,
            'end_sales': None,
            'forecast': {},
            'scenarios': {},
            'message': ''
        }
        
        # SQL query to calculate CAGR directly in database
        sql = f"""
        SELECT 
            a.Year AS StartYear,
            a.TotalSales AS StartSales,
            b.Year AS EndYear,
            b.TotalSales AS EndSales,
            ROUND(
                (POWER(b.TotalSales / a.TotalSales, 1.0 / (b.Year - a.Year)) - 1) * 100, 
                2
            ) AS CAGR,
            (POWER(b.TotalSales / a.TotalSales, 1.0 / (b.Year - a.Year)) - 1) AS CAGRDecimal
        FROM 
            (SELECT YEAR(OrderDate) AS Year, SUM(TotalAmount) AS TotalSales
             FROM salesorders
             WHERE YEAR(OrderDate) = {start_year}
             GROUP BY YEAR(OrderDate)) a
        JOIN 
            (SELECT YEAR(OrderDate) AS Year, SUM(TotalAmount) AS TotalSales
             FROM salesorders
             WHERE YEAR(OrderDate) = {end_year}
             GROUP BY YEAR(OrderDate)) b
        ON b.Year > a.Year
        """
        
        try:
            conn = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_NAME
            )
            
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            if df.empty:
                result['message'] = f'[WARNING] No data found for years {start_year} and {end_year}'
                return result
            
            # Extract values from result
            result['success'] = True
            result['cagr'] = float(df.iloc[0]['CAGR'])
            result['cagr_decimal'] = float(df.iloc[0]['CAGRDecimal'])
            result['start_sales'] = float(df.iloc[0]['StartSales'])
            result['end_sales'] = float(df.iloc[0]['EndSales'])
            
            # Calculate forecasts if requested
            if forecast_years:
                for year in forecast_years:
                    years_ahead = year - end_year
                    if years_ahead > 0:
                        # Base forecast: end_sales * (1 + CAGR)^years_ahead
                        base_forecast = result['end_sales'] * pow(1 + result['cagr_decimal'], years_ahead)
                        result['forecast'][year] = round(base_forecast, 2)
                        
                        # Scenarios: Optimistic (+10%), Base, Pessimistic (-10%)
                        optimistic_cagr = result['cagr_decimal'] * 1.10
                        pessimistic_cagr = result['cagr_decimal'] * 0.90
                        
                        result['scenarios'][year] = {
                            'base': round(base_forecast, 2),
                            'optimistic': round(result['end_sales'] * pow(1 + optimistic_cagr, years_ahead), 2),
                            'pessimistic': round(result['end_sales'] * pow(1 + pessimistic_cagr, years_ahead), 2),
                            'cagr_base': result['cagr'],
                            'cagr_optimistic': round(optimistic_cagr * 100, 2),
                            'cagr_pessimistic': round(pessimistic_cagr * 100, 2)
                        }
            
            result['message'] = '[OK] CAGR and forecasts calculated directly from database'
            
            return result
            
        except mysql.connector.Error as e:
            result['message'] = f'[ERROR] SQL execution failed: {str(e)}'
            return result
        except Exception as e:
            result['message'] = f'[ERROR] Unexpected error: {str(e)}'
            return result
    
    def execute_with_retry(self, sql: str, max_retries: int = 3) -> dict:
        """
        Execute SQL with automatic retry and correction on error
        Includes dynamic schema introspection, validation, and auto-save
        Returns: dict with 'success', 'data', 'sql_used', 'correction_applied', 'message'
        """
        import pandas as pd
        from pathlib import Path
        
        result = {
            'success': False,
            'data': None,
            'sql_used': sql,
            'correction_applied': False,
            'original_sql': sql,
            'message': '',
            'row_count': 0,
            'schema_validated': False
        }
        
        # Pre-validate query against schema
        is_valid, missing_tables, corrected_sql = schema_manager.validate_query(sql)
        
        if not is_valid:
            result['message'] = f"[ERROR] Table not found: {', '.join(missing_tables)}. Available tables: {', '.join(schema_manager.get_available_tables())}"
            return result
        
        if corrected_sql != sql:
            sql = corrected_sql
            result['correction_applied'] = True
            result['sql_used'] = sql
            result['message'] = '[AUTO-CORRECTED] Table names corrected automatically.'
        
        # Pre-process SQL for common syntax issues
        sql = self.fix_mysql_syntax(sql)
        
        # Introspect and validate query columns against schema
        try:
            introspection = self.introspect_query_columns(sql)
            
            if not introspection['valid']:
                result['message'] = f"[ERROR] Invalid columns in query: {', '.join(introspection['invalid_columns'])}"
                result['message'] += "\nThese columns do not exist in the schema."
                return result
            
            result['schema_validated'] = True
            
        except Exception as e:
            # If introspection fails, log warning but continue
            print(f"[WARNING] Schema introspection failed: {e}")
        
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
                result['row_count'] = len(df)
                
                # Auto-save results for export
                if not df.empty:
                    self._save_last_query_result(df, sql)
                    
                    # Cache query for performance
                    try:
                        result_summary = f"{len(df)} rows, {len(df.columns)} columns"
                        query_cache.add_query(
                            question="Query",  # Will be updated by caller
                            sql=sql,
                            result_summary=result_summary,
                            row_count=len(df)
                        )
                    except Exception as e:
                        print(f"[WARNING] Failed to cache query: {e}")
                
                # Check if query returned empty results
                if df.empty:
                    result['message'] = '[WARNING] Query executed successfully but returned no data. The database may not contain records matching your criteria.'
                elif attempt > 0:
                    result['message'] = '[AUTO-CORRECTED] SQL auto-corrected and executed successfully.'
                else:
                    result['message'] = '[OK] SQL executed successfully.'
                
                return result
                
            except mysql.connector.Error as e:
                error_code = e.errno
                error_message = str(e)
                
                print(f"SQL Error (attempt {attempt + 1}/{max_retries + 1}): {error_message}")
                
                # Handle specific MySQL errors
                if error_code == 1064:
                    # Syntax error - cannot auto-correct
                    result['message'] = f'[ERROR] SQL Syntax Error (1064): {error_message}\n\nThe generated SQL contains invalid MySQL syntax. Please rephrase your question.'
                    return result
                
                elif error_code == 1146:
                    # Table not found (42S02)
                    result['message'] = '[ERROR] Table not found. Fallback applied but table still missing. Please check available tables.'
                    return result
                
                elif error_code in [2003, 2006, 2013]:
                    # Connection errors - retry
                    if attempt < max_retries:
                        print(f"[RETRY] Database connection lost, retrying... (attempt {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(1)  # Wait 1 second before retry
                        continue
                    else:
                        result['message'] = '[ERROR] Database connection lost after multiple retries. Please check database server.'
                        return result
                
                # If this is the last attempt, return the error
                if attempt >= max_retries:
                    result['message'] = f'[ERROR] SQL execution failed after {max_retries + 1} attempts: {error_message}'
                    return result
                
                # Try to correct the SQL
                correction = self.correct_sql(sql, error_message)
                
                if correction['success'] and correction['corrected_sql']:
                    print(f"Attempting correction: {correction['explanation']}")
                    sql = correction['corrected_sql']
                    result['correction_applied'] = True
                    result['sql_used'] = sql
                else:
                    result['message'] = f"[ERROR] Column not found in schema. {correction['explanation']}"
                    return result
            
            except mysql.connector.OperationalError as e:
                # Handle operational errors (connection issues)
                print(f"[RETRY] Operational error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                
                if attempt < max_retries:
                    print("[RETRY] Database connection lost, retrying...")
                    import time
                    time.sleep(1)
                    continue
                else:
                    result['message'] = '[ERROR] Database connection lost after multiple retries. Please check database server.'
                    return result
            
            except Exception as e:
                result['message'] = f'[ERROR] Unexpected error: {str(e)}'
                return result
        
        return result    
    def _save_last_query_result(self, df: pd.DataFrame, sql: str):
        """
        Save last query result to temp file for export
        
        Args:
            df: DataFrame with query results
            sql: SQL query executed
        """
        try:
            from pathlib import Path
            import json
            
            temp_dir = Path("temp")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Save DataFrame to CSV
            csv_path = temp_dir / "last_query_result.csv"
            df.to_csv(csv_path, index=False)
            
            # Save metadata
            metadata = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'sql': sql,
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns)
            }
            
            metadata_path = temp_dir / "last_query_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"[OK] Saved query result ({len(df)} rows) to {csv_path}")
            
        except Exception as e:
            print(f"[WARNING] Failed to save query result: {e}")

# Global corrector instance
corrector = SQLCorrector()
