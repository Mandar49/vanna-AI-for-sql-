"""
Executive Intelligence Layer - Profile Manager (Phase 3B)
Multi-department memory contexts and persona linking.
Enables per-department intelligence and context persistence.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import threading


# Global state
ACTIVE_PROFILE: Optional[str] = None
PROFILES_DIR = "./profiles"
PROFILE_LOCK = threading.Lock()


def _ensure_profiles_dir() -> str:
    """Ensure profiles directory exists."""
    Path(PROFILES_DIR).mkdir(parents=True, exist_ok=True)
    return PROFILES_DIR


def _get_profile_dir(profile_name: str) -> str:
    """Get directory path for a specific profile."""
    return os.path.join(PROFILES_DIR, profile_name)


def _get_context_file(profile_name: str) -> str:
    """Get context JSONL file path for a profile."""
    return os.path.join(_get_profile_dir(profile_name), "context.jsonl")


def _get_metadata_file(profile_name: str) -> str:
    """Get metadata JSON file path for a profile."""
    return os.path.join(_get_profile_dir(profile_name), "metadata.json")


def init_profile(profile_name: str, persona: str = "Analyst") -> Dict[str, Any]:
    """
    Initialize a new profile with its own context storage.
    
    Args:
        profile_name: Name of the profile (e.g., "Sales", "Marketing", "HR")
        persona: Persona type (e.g., "Analyst", "Strategist", "Writer")
        
    Returns:
        Profile metadata dictionary
        
    Example:
        init_profile("Sales", persona="Analyst")
        init_profile("Marketing", persona="Strategist")
    """
    _ensure_profiles_dir()
    
    profile_dir = _get_profile_dir(profile_name)
    Path(profile_dir).mkdir(parents=True, exist_ok=True)
    
    # Create metadata
    metadata = {
        "name": profile_name,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "persona": persona,
        "last_accessed": datetime.now().isoformat(),
        "interaction_count": 0
    }
    
    # Save metadata
    metadata_file = _get_metadata_file(profile_name)
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # Create empty context file if it doesn't exist
    context_file = _get_context_file(profile_name)
    if not os.path.exists(context_file):
        Path(context_file).touch()
    
    print(f"✓ Profile '{profile_name}' initialized with persona '{persona}'")
    return metadata


def set_active_profile(profile_name: str) -> bool:
    """
    Set the active profile for the current session.
    
    Args:
        profile_name: Name of the profile to activate
        
    Returns:
        True if successful, False if profile doesn't exist
        
    Example:
        set_active_profile("Sales")
        # All subsequent operations use Sales profile
    """
    global ACTIVE_PROFILE
    
    # Check if profile exists
    profile_dir = _get_profile_dir(profile_name)
    if not os.path.exists(profile_dir):
        print(f"✗ Profile '{profile_name}' does not exist")
        return False
    
    with PROFILE_LOCK:
        ACTIVE_PROFILE = profile_name
    
    # Update last accessed time
    metadata_file = _get_metadata_file(profile_name)
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        metadata['last_accessed'] = datetime.now().isoformat()
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    print(f"✓ Active profile set to '{profile_name}'")
    return True


def get_active_profile() -> Optional[str]:
    """
    Get the currently active profile name.
    
    Returns:
        Active profile name or None if no profile is active
        
    Example:
        profile = get_active_profile()
        if profile:
            print(f"Current profile: {profile}")
    """
    with PROFILE_LOCK:
        return ACTIVE_PROFILE


def save_interaction(
    profile: str,
    query: str,
    response: str,
    sql: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Save an interaction to a profile's context history.
    
    Args:
        profile: Profile name
        query: User query
        response: System response
        sql: SQL query (optional)
        metadata: Additional metadata (optional)
        
    Returns:
        True if saved successfully
        
    Example:
        save_interaction(
            "Sales",
            "What are top products?",
            "Top products are...",
            sql="SELECT * FROM products ORDER BY sales DESC"
        )
    """
    # Ensure profile exists
    profile_dir = _get_profile_dir(profile)
    if not os.path.exists(profile_dir):
        print(f"✗ Profile '{profile}' does not exist. Creating it...")
        init_profile(profile)
    
    # Create interaction entry
    interaction = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response": response,
        "sql": sql,
        "metadata": metadata or {}
    }
    
    # Append to context file (JSONL format)
    context_file = _get_context_file(profile)
    with open(context_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(interaction) + '\n')
    
    # Update interaction count in metadata
    metadata_file = _get_metadata_file(profile)
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r', encoding='utf-8') as f:
            profile_metadata = json.load(f)
        profile_metadata['interaction_count'] = profile_metadata.get('interaction_count', 0) + 1
        profile_metadata['last_accessed'] = datetime.now().isoformat()
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(profile_metadata, f, indent=2)
    
    return True


def load_recent(profile: str, n: int = 10) -> List[Dict[str, Any]]:
    """
    Load recent interactions from a profile's context history.
    
    Args:
        profile: Profile name
        n: Number of recent interactions to load (default: 10)
        
    Returns:
        List of interaction dictionaries (most recent first)
        
    Example:
        recent = load_recent("Sales", n=5)
        for interaction in recent:
            print(f"Q: {interaction['query']}")
            print(f"A: {interaction['response']}")
    """
    context_file = _get_context_file(profile)
    
    if not os.path.exists(context_file):
        return []
    
    # Read all interactions
    interactions = []
    with open(context_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    interactions.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    # Return most recent n interactions (reversed)
    return interactions[-n:][::-1]


def list_profiles() -> List[Dict[str, Any]]:
    """
    List all available profiles with their metadata.
    
    Returns:
        List of profile metadata dictionaries
        
    Example:
        profiles = list_profiles()
        for profile in profiles:
            print(f"{profile['name']}: {profile['persona']}")
    """
    _ensure_profiles_dir()
    
    profiles = []
    
    # Scan profiles directory
    for item in os.listdir(PROFILES_DIR):
        profile_dir = os.path.join(PROFILES_DIR, item)
        if os.path.isdir(profile_dir):
            metadata_file = _get_metadata_file(item)
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    profiles.append(metadata)
            else:
                # Profile directory exists but no metadata
                profiles.append({
                    "name": item,
                    "created": "Unknown",
                    "persona": "Unknown",
                    "last_accessed": "Unknown",
                    "interaction_count": 0
                })
    
    # Sort by name
    profiles.sort(key=lambda x: x['name'])
    
    return profiles


def delete_profile(profile_name: str) -> bool:
    """
    Delete a profile and all its data.
    
    Args:
        profile_name: Name of the profile to delete
        
    Returns:
        True if deleted successfully, False if profile doesn't exist
        
    Example:
        if delete_profile("OldDepartment"):
            print("Profile deleted")
    """
    global ACTIVE_PROFILE
    
    profile_dir = _get_profile_dir(profile_name)
    
    if not os.path.exists(profile_dir):
        print(f"✗ Profile '{profile_name}' does not exist")
        return False
    
    # Clear active profile if it's the one being deleted
    with PROFILE_LOCK:
        if ACTIVE_PROFILE == profile_name:
            ACTIVE_PROFILE = None
    
    # Delete profile directory and all contents
    import shutil
    shutil.rmtree(profile_dir)
    
    print(f"✓ Profile '{profile_name}' deleted")
    return True


def get_profile_metadata(profile_name: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a specific profile.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        Profile metadata dictionary or None if not found
        
    Example:
        metadata = get_profile_metadata("Sales")
        print(f"Persona: {metadata['persona']}")
    """
    metadata_file = _get_metadata_file(profile_name)
    
    if not os.path.exists(metadata_file):
        return None
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_profile_stats(profile_name: str) -> Dict[str, Any]:
    """
    Get statistics for a profile.
    
    Args:
        profile_name: Name of the profile
        
    Returns:
        Dictionary with profile statistics
        
    Example:
        stats = get_profile_stats("Sales")
        print(f"Total interactions: {stats['total_interactions']}")
    """
    metadata = get_profile_metadata(profile_name)
    context_file = _get_context_file(profile_name)
    
    if not metadata:
        return {
            "exists": False,
            "total_interactions": 0,
            "file_size": 0
        }
    
    # Count interactions in context file
    interaction_count = 0
    if os.path.exists(context_file):
        with open(context_file, 'r', encoding='utf-8') as f:
            interaction_count = sum(1 for line in f if line.strip())
    
    file_size = os.path.getsize(context_file) if os.path.exists(context_file) else 0
    
    return {
        "exists": True,
        "name": metadata['name'],
        "persona": metadata['persona'],
        "created": metadata['created'],
        "last_accessed": metadata.get('last_accessed', 'Unknown'),
        "total_interactions": interaction_count,
        "file_size": file_size,
        "file_size_mb": round(file_size / (1024 * 1024), 2)
    }


if __name__ == "__main__":
    print("="*70)
    print("PROFILE MANAGER TEST")
    print("="*70)
    print()
    
    # Test 1: Initialize profiles
    print("1. Initializing profiles...")
    init_profile("Sales", persona="Analyst")
    init_profile("Marketing", persona="Strategist")
    init_profile("HR", persona="Writer")
    print()
    
    # Test 2: Set active profile
    print("2. Setting active profile...")
    set_active_profile("Sales")
    print(f"   Active profile: {get_active_profile()}")
    print()
    
    # Test 3: Save interactions
    print("3. Saving interactions...")
    save_interaction(
        "Sales",
        "What are our top products?",
        "Top products are Widget A, Widget B, and Widget C",
        sql="SELECT product, SUM(sales) FROM sales GROUP BY product ORDER BY SUM(sales) DESC LIMIT 3"
    )
    save_interaction(
        "Sales",
        "Show revenue by region",
        "Revenue by region: North $500K, South $450K, East $400K",
        sql="SELECT region, SUM(revenue) FROM sales GROUP BY region"
    )
    save_interaction(
        "Marketing",
        "What's our campaign performance?",
        "Campaign A: 15% CTR, Campaign B: 12% CTR",
        sql="SELECT campaign, AVG(ctr) FROM campaigns GROUP BY campaign"
    )
    print("   ✓ Interactions saved")
    print()
    
    # Test 4: Load recent interactions
    print("4. Loading recent interactions...")
    sales_recent = load_recent("Sales", n=5)
    print(f"   Sales profile has {len(sales_recent)} recent interactions")
    for i, interaction in enumerate(sales_recent, 1):
        print(f"   {i}. {interaction['query'][:50]}...")
    print()
    
    # Test 5: List all profiles
    print("5. Listing all profiles...")
    profiles = list_profiles()
    for profile in profiles:
        print(f"   • {profile['name']}: {profile['persona']} ({profile['interaction_count']} interactions)")
    print()
    
    # Test 6: Get profile stats
    print("6. Profile statistics...")
    stats = get_profile_stats("Sales")
    print(f"   Sales profile:")
    print(f"      Total interactions: {stats['total_interactions']}")
    print(f"      File size: {stats['file_size']} bytes")
    print(f"      Created: {stats['created']}")
    print()
    
    # Test 7: Switch profiles
    print("7. Switching profiles...")
    set_active_profile("Marketing")
    print(f"   Active profile: {get_active_profile()}")
    print()
    
    print("="*70)
    print("✅ Profile Manager ready")
    print("="*70)
