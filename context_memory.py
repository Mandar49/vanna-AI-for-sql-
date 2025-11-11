"""
Context Memory - Persistent conversation history with cognitive recall
Stores last 15 exchanges for context-aware reasoning
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class ContextMemory:
    def __init__(self, memory_dir: str = "memory", max_history: int = 15):
        self.memory_dir = memory_dir
        self.max_history = max_history
        self.history_file = os.path.join(memory_dir, "context_history.jsonl")
        
        # Create memory directory if it doesn't exist
        if not os.path.exists(memory_dir):
            os.makedirs(memory_dir)
            print(f"✓ Created memory directory: {memory_dir}")
        
        # Initialize history
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load conversation history from JSONL file"""
        if not os.path.exists(self.history_file):
            return []
        
        history = []
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        history.append(json.loads(line))
            
            # Keep only last max_history entries
            return history[-self.max_history:]
        except Exception as e:
            print(f"⚠ Warning: Could not load history: {e}")
            return []
    
    def _save_history(self):
        """Save conversation history to JSONL file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                for entry in self.history:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"⚠ Warning: Could not save history: {e}")
    
    def remember(self, query: str, response: str, sql: Optional[str] = None, 
                 insights: Optional[str] = None, persona: str = "Analyst"):
        """
        Store a new conversation exchange
        
        Args:
            query: User's question
            response: AI's response
            sql: SQL query used (if any)
            insights: Business insights generated
            persona: Persona used for response
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'sql': sql,
            'insights': insights,
            'persona': persona
        }
        
        self.history.append(entry)
        
        # Keep only last max_history entries
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Persist to disk
        self._save_history()
    
    def recall_context(self, last_n: int = 5) -> str:
        """
        Recall recent conversation context
        
        Args:
            last_n: Number of recent exchanges to recall
        
        Returns:
            Formatted text summary of recent context
        """
        if not self.history:
            return "No previous context available."
        
        recent = self.history[-last_n:]
        
        context_parts = ["Recent Conversation Context:"]
        for i, entry in enumerate(recent, 1):
            context_parts.append(f"\n[Exchange {i}]")
            context_parts.append(f"User: {entry['query']}")
            
            # Include SQL if available
            if entry.get('sql'):
                context_parts.append(f"SQL: {entry['sql'][:100]}...")
            
            # Include brief response
            response_preview = entry['response'][:150] + "..." if len(entry['response']) > 150 else entry['response']
            context_parts.append(f"AI: {response_preview}")
        
        return "\n".join(context_parts)
    
    def get_last_query(self) -> Optional[Dict]:
        """Get the most recent query"""
        return self.history[-1] if self.history else None
    
    def get_related_context(self, current_query: str, max_results: int = 3) -> List[Dict]:
        """
        Find related previous exchanges based on keyword matching
        
        Args:
            current_query: Current user query
            max_results: Maximum number of related exchanges to return
        
        Returns:
            List of related conversation entries
        """
        if not self.history:
            return []
        
        # Simple keyword-based matching
        query_lower = current_query.lower()
        keywords = set(query_lower.split())
        
        scored_entries = []
        for entry in self.history:
            entry_keywords = set(entry['query'].lower().split())
            overlap = len(keywords & entry_keywords)
            if overlap > 0:
                scored_entries.append((overlap, entry))
        
        # Sort by relevance and return top results
        scored_entries.sort(reverse=True, key=lambda x: x[0])
        return [entry for _, entry in scored_entries[:max_results]]
    
    def clear_memory(self):
        """Clear all conversation history"""
        self.history = []
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
        print("✓ Memory cleared")
    
    def get_statistics(self) -> Dict:
        """Get memory statistics"""
        return {
            'total_exchanges': len(self.history),
            'max_capacity': self.max_history,
            'memory_file': self.history_file,
            'oldest_entry': self.history[0]['timestamp'] if self.history else None,
            'newest_entry': self.history[-1]['timestamp'] if self.history else None
        }

# Global memory instance
memory = ContextMemory()
