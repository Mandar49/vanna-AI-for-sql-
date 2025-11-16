"""
Query Cache - Cache recent queries for performance optimization
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class QueryCache:
    def __init__(self, cache_dir: str = "cache", max_entries: int = 5):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "query_history.json")
        self.max_entries = max_entries
        
        # Create cache directory
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        
        self.cache = self._load_cache()
    
    def _load_cache(self) -> List[Dict]:
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WARNING] Failed to load query cache: {e}")
        
        return []
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"[WARNING] Failed to save query cache: {e}")
    
    def add_query(self, question: str, sql: str, result_summary: str, 
                  row_count: int = 0):
        """
        Add query to cache
        
        Args:
            question: User's question
            sql: SQL query executed
            result_summary: Summary of results
            row_count: Number of rows returned
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'sql': sql,
            'result_summary': result_summary,
            'row_count': row_count
        }
        
        # Add to beginning of cache
        self.cache.insert(0, entry)
        
        # Keep only max_entries
        self.cache = self.cache[:self.max_entries]
        
        self._save_cache()
    
    def get_recent_queries(self, n: int = 5) -> List[Dict]:
        """Get n most recent queries"""
        return self.cache[:n]
    
    def search_cache(self, question: str) -> Optional[Dict]:
        """
        Search cache for similar question
        
        Args:
            question: Question to search for
        
        Returns:
            Cached entry if found, None otherwise
        """
        question_lower = question.lower()
        
        for entry in self.cache:
            if entry['question'].lower() == question_lower:
                return entry
        
        return None
    
    def clear_cache(self):
        """Clear all cached queries"""
        self.cache = []
        self._save_cache()
        print("[OK] Query cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_queries': len(self.cache),
            'max_entries': self.max_entries,
            'cache_file': self.cache_file,
            'oldest_query': self.cache[-1]['timestamp'] if self.cache else None,
            'newest_query': self.cache[0]['timestamp'] if self.cache else None
        }

# Global query cache instance
query_cache = QueryCache()
