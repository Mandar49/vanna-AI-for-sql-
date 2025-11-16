"""
Error Logger - Centralized error logging for SQL and application errors
"""
import os
from datetime import datetime
from pathlib import Path

class ErrorLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        self.error_log = os.path.join(log_dir, "errors.log")
    
    def log_sql_error(self, error_type: str, sql: str, error_message: str, 
                     question: str = None, context: dict = None):
        """
        Log SQL-related errors
        
        Args:
            error_type: Type of error (SYNTAX, EMPTY_RESULT, EXECUTION, etc.)
            sql: SQL query that caused the error
            error_message: Error message
            question: User's original question (optional)
            context: Additional context (optional)
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = [
                f"\n{'='*70}",
                f"[{timestamp}] SQL ERROR: {error_type}",
                f"{'='*70}"
            ]
            
            if question:
                log_entry.append(f"Question: {question}")
            
            log_entry.append(f"\nSQL Query:\n{sql}")
            log_entry.append(f"\nError Message:\n{error_message}")
            
            if context:
                log_entry.append(f"\nContext:")
                for key, value in context.items():
                    log_entry.append(f"  {key}: {value}")
            
            log_entry.append(f"{'='*70}\n")
            
            with open(self.error_log, 'a', encoding='utf-8') as f:
                f.write('\n'.join(log_entry))
        
        except Exception as e:
            print(f"Warning: Could not write to error log: {e}")
    
    def log_application_error(self, error_type: str, error_message: str, 
                             context: dict = None):
        """
        Log general application errors
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context (optional)
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            log_entry = [
                f"\n{'='*70}",
                f"[{timestamp}] APPLICATION ERROR: {error_type}",
                f"{'='*70}",
                f"Error Message:\n{error_message}"
            ]
            
            if context:
                log_entry.append(f"\nContext:")
                for key, value in context.items():
                    log_entry.append(f"  {key}: {value}")
            
            log_entry.append(f"{'='*70}\n")
            
            with open(self.error_log, 'a', encoding='utf-8') as f:
                f.write('\n'.join(log_entry))
        
        except Exception as e:
            print(f"Warning: Could not write to error log: {e}")
    
    def get_recent_errors(self, n: int = 10) -> list:
        """
        Get the most recent error entries
        
        Args:
            n: Number of recent errors to retrieve
        
        Returns:
            List of error entries
        """
        try:
            if not os.path.exists(self.error_log):
                return []
            
            with open(self.error_log, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by separator
            entries = content.split('='*70)
            # Filter out empty entries
            entries = [e.strip() for e in entries if e.strip()]
            
            # Return last n entries
            return entries[-n:] if len(entries) > n else entries
        
        except Exception as e:
            print(f"Warning: Could not read error log: {e}")
            return []
    
    def clear_log(self):
        """Clear the error log"""
        try:
            if os.path.exists(self.error_log):
                os.remove(self.error_log)
        except Exception as e:
            print(f"Warning: Could not clear error log: {e}")

# Global error logger instance
error_logger = ErrorLogger()
