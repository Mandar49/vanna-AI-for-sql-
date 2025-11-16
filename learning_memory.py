"""
Executive Intelligence Layer - Auto Learning Memory (Phase 5G)
Self-improving reasoning system with offline adaptive memory.
Learns from successful commands and user feedback to improve over time.
"""

import os
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

# Memory directory
MEMORY_DIR = "./memory"
LEARNING_FILE = os.path.join(MEMORY_DIR, "learning.jsonl")
PATTERNS_FILE = os.path.join(MEMORY_DIR, "patterns.json")
TEMPLATES_FILE = os.path.join(MEMORY_DIR, "templates.json")

# Thread lock for file operations
MEMORY_LOCK = threading.Lock()

# In-memory cache
_learning_cache = []
_patterns_cache = {}
_templates_cache = {}


def _ensure_memory_dir():
    """Ensure memory directory exists."""
    Path(MEMORY_DIR).mkdir(parents=True, exist_ok=True)


def log_success(query: str, result: Dict[str, Any], feedback: Optional[str] = None) -> bool:
    """
    Log a successful command execution for learning.
    
    Args:
        query: The command/query that was executed
        result: The result dictionary from execution
        feedback: Optional user feedback (positive/negative/neutral)
        
    Returns:
        True if logged successfully
        
    Example:
        log_success(
            query="analyze KPIs for Sales",
            result={"status": "success", "message": "Analysis complete"},
            feedback="positive"
        )
    """
    try:
        _ensure_memory_dir()
        
        # Create learning entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "result": {
                "status": result.get("status"),
                "message": result.get("message"),
                "action": result.get("intent", {}).get("action") if "intent" in result else None
            },
            "feedback": feedback or "neutral",
            "success": result.get("status") == "success"
        }
        
        with MEMORY_LOCK:
            # Append to JSONL file
            with open(LEARNING_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
            
            # Update cache
            _learning_cache.append(entry)
            
            # Keep cache size manageable
            if len(_learning_cache) > 1000:
                _learning_cache.pop(0)
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to log success: {e}")
        return False


def learn_from_feedback() -> Dict[str, Any]:
    """
    Analyze logged feedback and adjust prompt templates.
    
    This function:
    1. Loads all learning entries
    2. Identifies successful patterns
    3. Updates prompt templates based on patterns
    4. Returns learning statistics
    
    Returns:
        Dictionary with learning statistics and improvements
        
    Example:
        stats = learn_from_feedback()
        print(f"Learned from {stats['entries_analyzed']} entries")
        print(f"Identified {stats['patterns_found']} patterns")
    """
    try:
        _ensure_memory_dir()
        
        # Load all learning entries
        entries = load_learning_history()
        
        if not entries:
            return {
                "status": "no_data",
                "message": "No learning data available",
                "entries_analyzed": 0,
                "patterns_found": 0
            }
        
        # Analyze patterns
        patterns = _analyze_patterns(entries)
        
        # Update templates based on patterns
        templates_updated = _update_templates(patterns)
        
        # Save patterns
        _save_patterns(patterns)
        
        # Calculate statistics
        total_entries = len(entries)
        successful_entries = sum(1 for e in entries if e.get("success"))
        positive_feedback = sum(1 for e in entries if e.get("feedback") == "positive")
        
        return {
            "status": "success",
            "message": "Learning complete",
            "entries_analyzed": total_entries,
            "successful_entries": successful_entries,
            "positive_feedback": positive_feedback,
            "patterns_found": len(patterns),
            "templates_updated": templates_updated,
            "success_rate": successful_entries / total_entries if total_entries > 0 else 0
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Learning failed: {str(e)}",
            "entries_analyzed": 0,
            "patterns_found": 0
        }


def load_learning_history(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Load learning history from JSONL file.
    
    Args:
        limit: Optional limit on number of entries to return (most recent)
        
    Returns:
        List of learning entries
        
    Example:
        history = load_learning_history(limit=100)
        for entry in history:
            print(f"{entry['query']} → {entry['result']['status']}")
    """
    try:
        _ensure_memory_dir()
        
        if not os.path.exists(LEARNING_FILE):
            return []
        
        entries = []
        
        with MEMORY_LOCK:
            with open(LEARNING_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        
        # Return most recent entries if limit specified
        if limit:
            return entries[-limit:]
        
        return entries
        
    except Exception as e:
        print(f"✗ Failed to load learning history: {e}")
        return []


def get_learning_stats() -> Dict[str, Any]:
    """
    Get statistics about learning memory.
    
    Returns:
        Dictionary with learning statistics
        
    Example:
        stats = get_learning_stats()
        print(f"Total entries: {stats['total_entries']}")
        print(f"Success rate: {stats['success_rate']:.2%}")
    """
    try:
        entries = load_learning_history()
        
        if not entries:
            return {
                "total_entries": 0,
                "successful_entries": 0,
                "failed_entries": 0,
                "success_rate": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "patterns_identified": 0
            }
        
        successful = sum(1 for e in entries if e.get("success"))
        failed = len(entries) - successful
        positive = sum(1 for e in entries if e.get("feedback") == "positive")
        negative = sum(1 for e in entries if e.get("feedback") == "negative")
        
        # Load patterns
        patterns = _load_patterns()
        
        return {
            "total_entries": len(entries),
            "successful_entries": successful,
            "failed_entries": failed,
            "success_rate": successful / len(entries) if entries else 0,
            "positive_feedback": positive,
            "negative_feedback": negative,
            "patterns_identified": len(patterns),
            "last_learning": entries[-1]["timestamp"] if entries else None
        }
        
    except Exception as e:
        print(f"✗ Failed to get learning stats: {e}")
        return {}


def get_successful_patterns(action: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get successful command patterns for learning.
    
    Args:
        action: Optional action filter (e.g., "analyze_kpis", "generate_report")
        
    Returns:
        List of successful patterns
        
    Example:
        patterns = get_successful_patterns(action="analyze_kpis")
        for pattern in patterns:
            print(f"Query: {pattern['query']}")
            print(f"Success count: {pattern['count']}")
    """
    try:
        patterns = _load_patterns()
        
        if action:
            return [p for p in patterns if p.get("action") == action]
        
        return patterns
        
    except Exception as e:
        print(f"✗ Failed to get patterns: {e}")
        return []


def suggest_improvement(query: str) -> Optional[str]:
    """
    Suggest an improved version of a query based on learned patterns.
    
    Args:
        query: The query to improve
        
    Returns:
        Suggested improved query or None
        
    Example:
        improved = suggest_improvement("show me sales data")
        # Returns: "analyze KPIs for Sales"
    """
    try:
        patterns = _load_patterns()
        
        # Find similar successful patterns
        query_lower = query.lower()
        
        for pattern in patterns:
            if pattern.get("success_rate", 0) > 0.8:  # High success rate
                # Check for keyword matches
                pattern_keywords = set(pattern.get("keywords", []))
                query_keywords = set(query_lower.split())
                
                # If significant overlap, suggest the pattern
                overlap = len(pattern_keywords & query_keywords)
                if overlap >= 2:
                    return pattern.get("example_query")
        
        return None
        
    except Exception as e:
        print(f"✗ Failed to suggest improvement: {e}")
        return None


def clear_learning_memory() -> bool:
    """
    Clear all learning memory (use with caution).
    
    Returns:
        True if cleared successfully
    """
    try:
        with MEMORY_LOCK:
            if os.path.exists(LEARNING_FILE):
                os.remove(LEARNING_FILE)
            if os.path.exists(PATTERNS_FILE):
                os.remove(PATTERNS_FILE)
            if os.path.exists(TEMPLATES_FILE):
                os.remove(TEMPLATES_FILE)
            
            _learning_cache.clear()
            _patterns_cache.clear()
            _templates_cache.clear()
        
        print("✓ Learning memory cleared")
        return True
        
    except Exception as e:
        print(f"✗ Failed to clear memory: {e}")
        return False


# Helper functions

def _analyze_patterns(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze entries to identify successful patterns."""
    patterns = defaultdict(lambda: {
        "count": 0,
        "success_count": 0,
        "queries": [],
        "keywords": set()
    })
    
    for entry in entries:
        if not entry.get("success"):
            continue
        
        action = entry.get("result", {}).get("action")
        if not action:
            continue
        
        # Track pattern
        pattern = patterns[action]
        pattern["count"] += 1
        pattern["success_count"] += 1
        pattern["queries"].append(entry["query"])
        
        # Extract keywords
        query_words = entry["query"].lower().split()
        pattern["keywords"].update(query_words)
    
    # Convert to list format
    result = []
    for action, data in patterns.items():
        if data["count"] >= 2:  # Minimum 2 occurrences
            result.append({
                "action": action,
                "count": data["count"],
                "success_count": data["success_count"],
                "success_rate": data["success_count"] / data["count"],
                "example_query": data["queries"][0] if data["queries"] else None,
                "keywords": list(data["keywords"])[:10]  # Top 10 keywords
            })
    
    # Sort by success count
    result.sort(key=lambda x: x["success_count"], reverse=True)
    
    return result


def _update_templates(patterns: List[Dict[str, Any]]) -> int:
    """Update prompt templates based on patterns."""
    try:
        templates = _load_templates()
        
        updated_count = 0
        
        for pattern in patterns:
            action = pattern["action"]
            
            # Create or update template
            if action not in templates or pattern["success_rate"] > templates[action].get("success_rate", 0):
                templates[action] = {
                    "example": pattern["example_query"],
                    "keywords": pattern["keywords"],
                    "success_rate": pattern["success_rate"],
                    "updated_at": datetime.now().isoformat()
                }
                updated_count += 1
        
        # Save templates
        _save_templates(templates)
        
        return updated_count
        
    except Exception as e:
        print(f"✗ Failed to update templates: {e}")
        return 0


def _load_patterns() -> List[Dict[str, Any]]:
    """Load patterns from file."""
    try:
        if not os.path.exists(PATTERNS_FILE):
            return []
        
        with open(PATTERNS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []


def _save_patterns(patterns: List[Dict[str, Any]]):
    """Save patterns to file."""
    try:
        _ensure_memory_dir()
        
        with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
    except Exception as e:
        print(f"✗ Failed to save patterns: {e}")


def _load_templates() -> Dict[str, Any]:
    """Load templates from file."""
    try:
        if not os.path.exists(TEMPLATES_FILE):
            return {}
        
        with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def _save_templates(templates: Dict[str, Any]):
    """Save templates to file."""
    try:
        _ensure_memory_dir()
        
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2)
    except Exception as e:
        print(f"✗ Failed to save templates: {e}")


if __name__ == "__main__":
    print("="*70)
    print("AUTO LEARNING MEMORY TEST")
    print("="*70)
    print()
    
    # Test 1: Initialize
    print("1. Initializing learning memory...")
    _ensure_memory_dir()
    print(f"   ✓ Memory directory: {MEMORY_DIR}")
    print()
    
    # Test 2: Log successes
    print("2. Logging successful commands...")
    
    test_commands = [
        ("list profiles", {"status": "success", "message": "Found 7 profiles", "intent": {"action": "list_profiles"}}, "positive"),
        ("analyze KPIs for Sales", {"status": "success", "message": "Analysis complete", "intent": {"action": "analyze_kpis"}}, "positive"),
        ("generate report for Marketing", {"status": "success", "message": "Report generated", "intent": {"action": "generate_report"}}, "positive"),
        ("analyze KPIs for Finance", {"status": "success", "message": "Analysis complete", "intent": {"action": "analyze_kpis"}}, "positive"),
    ]
    
    for query, result, feedback in test_commands:
        success = log_success(query, result, feedback)
        if success:
            print(f"   ✓ Logged: {query}")
    print()
    
    # Test 3: Get statistics
    print("3. Getting learning statistics...")
    stats = get_learning_stats()
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Successful: {stats['successful_entries']}")
    print(f"   Success rate: {stats['success_rate']:.2%}")
    print(f"   Positive feedback: {stats['positive_feedback']}")
    print()
    
    # Test 4: Learn from feedback
    print("4. Learning from feedback...")
    learning_result = learn_from_feedback()
    print(f"   Status: {learning_result['status']}")
    print(f"   Entries analyzed: {learning_result['entries_analyzed']}")
    print(f"   Patterns found: {learning_result['patterns_found']}")
    print(f"   Templates updated: {learning_result['templates_updated']}")
    print()
    
    # Test 5: Get patterns
    print("5. Getting successful patterns...")
    patterns = get_successful_patterns()
    print(f"   Patterns identified: {len(patterns)}")
    for pattern in patterns[:3]:
        print(f"   • {pattern['action']}: {pattern['success_count']} successes ({pattern['success_rate']:.0%})")
    print()
    
    # Test 6: Suggest improvement
    print("6. Testing query improvement...")
    test_query = "show me KPIs"
    suggestion = suggest_improvement(test_query)
    if suggestion:
        print(f"   Query: '{test_query}'")
        print(f"   Suggestion: '{suggestion}'")
    else:
        print(f"   No suggestion for: '{test_query}'")
    print()
    
    print("="*70)
    print("✅ Auto Learning Memory ready")
    print("="*70)
