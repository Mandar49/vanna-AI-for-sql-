"""
Schema Manager - Intelligent schema caching and query rewriting
Handles missing tables, validates columns, and provides fallback strategies
"""
import re
import json
import os
import mysql.connector
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class SchemaManager:
    def __init__(self, cache_dir: str = "cache", log_dir: str = "logs"):
        self.cache_dir = cache_dir
        self.log_dir = log_dir
        self.schema_cache_file = os.path.join(cache_dir, "schema_cache.json")
        self.rewrite_log_file = os.path.join(log_dir, "query_rewrites.log")
        
        # Create directories
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        self.schema_cache = {}
        self.table_aliases = {}
        self.load_schema_cache()
    
    def load_schema_cache(self) -> bool:
        """
        Load schema from cache or query database if cache is stale/missing
        
        Returns:
            True if schema loaded successfully
        """
        # Try to load from cache first
        if os.path.exists(self.schema_cache_file):
            try:
                with open(self.schema_cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is recent (less than 24 hours old)
                cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2000-01-01'))
                age_hours = (datetime.now() - cache_time).total_seconds() / 3600
                
                if age_hours < 24:
                    self.schema_cache = cached_data.get('schema', {})
                    self.table_aliases = cached_data.get('aliases', {})
                    print(f"[OK] Loaded schema cache ({len(self.schema_cache)} tables)")
                    return True
            except Exception as e:
                print(f"[WARNING] Failed to load cache: {e}")
        
        # Cache miss or stale - query database
        return self.refresh_schema_cache()
    
    def refresh_schema_cache(self) -> bool:
        """
        Query database and refresh schema cache
        
        Returns:
            True if schema refreshed successfully
        """
        try:
            from common import AppConfig
            
            conn = mysql.connector.connect(
                host=AppConfig.DB_HOST,
                user=AppConfig.DB_USER,
                password=AppConfig.DB_PASSWORD,
                database=AppConfig.DB_NAME
            )
            cursor = conn.cursor()
            
            # Query INFORMATION_SCHEMA for complete schema
            cursor.execute("""
                SELECT 
                    TABLE_NAME,
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_KEY
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """, (AppConfig.DB_NAME,))
            
            schema = {}
            for table_name, column_name, data_type, is_nullable, column_key in cursor.fetchall():
                if table_name not in schema:
                    schema[table_name] = {
                        'columns': [],
                        'primary_keys': [],
                        'nullable_columns': []
                    }
                
                schema[table_name]['columns'].append({
                    'name': column_name,
                    'type': data_type,
                    'nullable': is_nullable == 'YES'
                })
                
                if column_key == 'PRI':
                    schema[table_name]['primary_keys'].append(column_name)
                
                if is_nullable == 'YES':
                    schema[table_name]['nullable_columns'].append(column_name)
            
            cursor.close()
            conn.close()
            
            self.schema_cache = schema
            self._build_table_aliases()
            self._save_schema_cache()
            
            print(f"[OK] Refreshed schema cache ({len(schema)} tables)")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to refresh schema: {e}")
            return False
    
    def _build_table_aliases(self):
        """Build common table name aliases for fallback"""
        self.table_aliases = {}
        
        for table_name in self.schema_cache.keys():
            # Add lowercase version
            self.table_aliases[table_name.lower()] = table_name
            
            # Add common variations
            if 'order' in table_name.lower():
                self.table_aliases['orders'] = table_name
                self.table_aliases['order'] = table_name
            
            if 'customer' in table_name.lower():
                self.table_aliases['customers'] = table_name
                self.table_aliases['customer'] = table_name
            
            if 'product' in table_name.lower():
                self.table_aliases['products'] = table_name
                self.table_aliases['product'] = table_name
            
            if 'sales' in table_name.lower():
                self.table_aliases['sales'] = table_name
                self.table_aliases['sale'] = table_name
    
    def _save_schema_cache(self):
        """Save schema cache to file"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'schema': self.schema_cache,
                'aliases': self.table_aliases
            }
            
            with open(self.schema_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        
        except Exception as e:
            print(f"[WARNING] Failed to save cache: {e}")
    
    def validate_query(self, sql: str) -> Tuple[bool, List[str], str]:
        """
        Validate SQL query against schema
        
        Args:
            sql: SQL query to validate
        
        Returns:
            Tuple of (is_valid, missing_tables, corrected_sql)
        """
        missing_tables = []
        corrections = []
        
        # Extract table names from SQL
        table_pattern = r'\bFROM\s+(\w+)|JOIN\s+(\w+)'
        matches = re.findall(table_pattern, sql, re.IGNORECASE)
        
        for match in matches:
            table_name = match[0] or match[1]
            
            # Check if table exists
            if table_name not in self.schema_cache:
                # Try to find alias or similar table
                corrected_table = self._find_table_fallback(table_name)
                
                if corrected_table:
                    sql = re.sub(
                        rf'\b{table_name}\b',
                        corrected_table,
                        sql,
                        flags=re.IGNORECASE
                    )
                    corrections.append(f"{table_name} → {corrected_table}")
                else:
                    missing_tables.append(table_name)
        
        # Log corrections
        if corrections:
            self._log_rewrite(sql, corrections)
        
        is_valid = len(missing_tables) == 0
        return is_valid, missing_tables, sql
    
    def _find_table_fallback(self, table_name: str) -> Optional[str]:
        """
        Find fallback table for missing table name
        
        Args:
            table_name: Missing table name
        
        Returns:
            Corrected table name or None
        """
        # Check aliases
        if table_name.lower() in self.table_aliases:
            return self.table_aliases[table_name.lower()]
        
        # Check for partial matches
        table_lower = table_name.lower()
        for actual_table in self.schema_cache.keys():
            if table_lower in actual_table.lower() or actual_table.lower() in table_lower:
                return actual_table
        
        # Common fallbacks
        fallback_map = {
            'sales_2024': 'salesorders',
            'sales_2023': 'salesorders',
            'orders_2024': 'salesorders',
            'orders_2023': 'salesorders',
            'order_items': 'orderitems',
            'order_details': 'orderitems',
            'customer_list': 'customers',
            'product_list': 'products'
        }
        
        return fallback_map.get(table_lower)
    
    def _log_rewrite(self, sql: str, corrections: List[str]):
        """Log query rewrites"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"\n[{timestamp}] Query Rewrite\n"
            log_entry += f"Corrections: {', '.join(corrections)}\n"
            log_entry += f"SQL: {sql[:200]}...\n"
            log_entry += "="*70 + "\n"
            
            with open(self.rewrite_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        
        except Exception as e:
            print(f"[WARNING] Failed to log rewrite: {e}")
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """Get column names for a table"""
        if table_name in self.schema_cache:
            return [col['name'] for col in self.schema_cache[table_name]['columns']]
        return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in schema"""
        return table_name in self.schema_cache
    
    def get_available_tables(self) -> List[str]:
        """Get list of all available tables"""
        return list(self.schema_cache.keys())

# Global schema manager instance
schema_manager = SchemaManager()
